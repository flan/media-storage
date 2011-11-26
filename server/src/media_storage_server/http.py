"""
Provides all resources needed for the HTTP interface.
"""
import base64
import collections
import json
import logging
import os
import random
import tempfile
import threading
import time
import traceback
import uuid

import tornado.ioloop
import tornado.web

from config import CONFIG
import compression
import database
import filesystem
import state

_CHUNK_SIZE = 16 * 1024 #Write 16k at a time.
_TEMPFILE_THRESHOLD = 128 * 1024 #Buffer up to 128k in memory

_TrustLevel = collections.namedtuple('TrustLevel', ('read', 'write',))

_logger = logging.getLogger("media_storage.http")

def _get_trust(record, keys, host):
    """
    Record and keys can be None to skip that check.
    Keys may be omitted by a requestor.
    Either key may be omitted, too.
    """
    for trusted in CONFIG.security_trusted_hosts.split():
        if host == trusted:
            return _TrustLevel(True, True)
            
    if keys:
        return _TrustLevel(
         record['key']['read'] in (keys.get('read'), None),
         record['key']['write'] in (keys.get('write'), None),
        )
        
    return _TrustLevel(
     record['key']['read'] is None,
     record['key']['write'] is None,
    )
    
def _get_json(body):
    try:
        return json.loads(body or 'null')
    except ValueError as e:
        _logger.warn(str(e))
        raise
        
def _get_payload(body):
    """
    Depending on whether the request came through an nginx proxy, this will determine the right
    way to expose the received data. Regardless of path, the values returned will be a JSON
    object descriptor and a file-like object containing the submitted bytes.
    """
    if False: #nginx proxy
        return ({}, None)
    else:
        divider = body.find('\0')
        
        header = _get_json(body[:divider])
        
        content = tempfile.SpooledTemporaryFile(_TEMPFILE_THRESHOLD)
        content.write(body[divider + 1:])
        content.flush()
        content.seek(0)
        
        return (header, content)
        
        
class BaseHandler(tornado.web.RequestHandler):
    """
    A generalised request-handler for inbound communication.
    
    Responds with one of the following codes::
    
    - 200 if everything went well
    - 404 if the requested resource was unavailable
    - 409 if the request made no sense
    - 500 if an internal exception happened
    - 503 if a short-term problem occurred
    """
    def get(self):
        """
        Handles an HTTP GET request.
        """
        _logger.debug("Received an HTTP GET request for '%(path)s'" % {
         'path': self.request.path,
        })
        output = self._get()
        if not output is None:
            self.write(output)
            self.finish()
            
    def _get(self):
        """
        Returns the current time; override this to do useful things.
        """
        return {
         'timestamp': int(time.time()),
         'note': "This timestamp is in UTC",
        }
        
    def post(self):
        """
        Handles an HTTP POST request.
        """
        _logger.debug("Received an HTTP POST request for '%(path)s'" % {
         'path': self.request.path,
        })
        output = self._post()
        if not output is None:
            self.write(output)
            self.finish()
            
    def _post(self):
        """
        Returns the current time; override this to do useful things.
        """
        return {
         'timestamp': int(time.time()),
         'note': "This timestamp is in UTC; thanks for POSTing",
        }
        
class GetHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        
        record = database.get_record(request['uid'])
        if not record:
            self.send_error(404)
            
        trust = _get_trust(record, request.get('key'), self.request.remote_ip)
        if not trust.read:
            self.send_error(403)
            return
            
        fs = state.get_filesystem(record['physical']['family'])
        try:
            data = fs.get(record)
        except filesystem.FileNotFoundError as e:
            #log
            self.send_error(404)
        else:
            applied_compression = record['physical']['format'].get('comp')
            supported_compressions = (c.strip() for c in (self.request.headers.get('Media-Storage-Supported-Compression') or '').split(';'))
            if applied_compression and not applied_compression in supported_compressions: #Must be decompressed first
                #log
                decompressor = getattr(compression, 'decompress_' + applied_compression)
                data = decompressor(data)
                applied_compression = None
                
            self.headers['Content-Type'] = record['physical']['format']['mime']
            self.headers['Content-Length'] = str(filesystem.file_size(record))
            if applied_compression:
                self.headers['Ivr-Applied-Compression'] = applied_compression
            while True:
                chunk = data.read(_CHUNK_SIZE)
                if chunk:
                    self.write(chunk)
                    self.flush()
                else:
                    break
            self.finish()
            
class DescribeHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        
        record = database.get_record(request['uid'])
        if not record:
            self.send_error(404)
            
        trust = _get_trust(record, request.get('key'), self.request.remote_ip)
        if not trust.read:
            self.send_error(403)
            return
            
        del record['physical']['minRes']
        del record['key']
        self.write(record)
        self.finish()
        
class QueryHandler(BaseHandler):
    def _post(self):
        request = _get_json(self.request.body)
        
        trust = _get_trust(None, None, self.request.remote_ip)
        #Issue the query; if not trust.read, only return matching records with key.read=None
        pass
        
class PutHandler(BaseHandler):
    def _post(self):
        (header, data) = _get_payload(self.request.body)
        
        current_time = time.time()
        try:
            format = {
             'mime': header['physical']['format']['mime'],
            }
            target_compression = header['physical']['format'].get('comp')
            if target_compression:
                if self.request.headers.get('Media-Storage-Compress-On-Server') == 'yes':
                    compressor = getattr(compression, 'compress_' + target_compression)
                    data = compressor(data)
                format['comp'] = target_compression
            extension = header['physical']['format'].get('ext')
            if extension:
                format['ext'] = extension
                
            policy = {
             'delete': {},
             'compress': {},
            }
            header_policy = header.get('policy')
            if header_policy:
                delete_policy = header_policy.get('delete')
                if delete_policy:
                    delete_expiration = delete_policy.get('fixed')
                    if delete_expiration:
                        policy['delete']['fixed'] = int(current_time + delete_expiration)
                    delete_stale = delete_policy.get('stale')
                    if delete_stale:
                        policy['delete']['stale'] = int(delete_stale)
                        
                compress_policy = header_policy.get('compress')
                if compress_policy:
                    compress_format = compress_policy.get('comp')
                    if compress_format in ('gz', 'bz2', 'lzma'): #TODO: make this dynamic
                        policy['compress']['comp'] = compress_format
                        compress_expiration = compress_policy.get('fixed')
                        if compress_expiration:
                            policy['compress']['fixed'] = int(current_time + compress_expiration)
                        compress_stale = compress_policy.get('stale')
                        if compress_stale:
                            policy['compress']['stale'] = int(compress_stale)
                    else:
                        #log
                        
            record = {
             '_id': header.get('uid') or uuid.uuid1().hex,
             'key': header.get('key') or {
              'read': base64.urlsafe_b64encode(os.urandom(random.randint(10, 20)))[:-2],
              'write': base64.urlsafe_b64encode(os.urandom(random.randint(10, 20)))[:-2],
             },
             'physical': {
              'family': header['physical'].get('family'),
              'ctime': current_time,
              'minRes': CONFIG.storage_minute_resolution,
              'atime': int(current_time),
              'format': format,
             },
             'policy': policy,
             'stats': {
              'accesses': 0,
             },
             'meta': header.get('meta') or {},
            }
        except KeyError as e:
            #log
            self.send_error(409)
            return
            
        print record
        print repr(data.read())
        database.put_record(record)
        fs = state.get_filesystem(record['physical']['family'])
        fs.put(record, data)
        
        return {
         'uid': record['_id'],
         'key': record['key'],
        }
        
class UnlinkHandler(BaseHandler):
    def _get(self):
        request = _get_json(self.request.body)
        uid = request['uid']
        
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            
        trust = _get_trust(record, request.get('key'), self.request.remote_ip)
        if not trust.write:
            self.send_error(403)
            return
        
        fs = state.get_filesystem(record['physical']['family'])
        try:
            fs.unlink(record)
        except filesystem.FileNotFoundError as e:
            self.send_error(404)
        else:
            database.drop_record(uid)
            
            
class HTTPService(threading.Thread):
    """
    A threaded handler for HTTP requests, so that client interaction can happen in parallel with
    other processing.
    
    Starts with `start()` and executes until `kill()` is invoked.
    """
    _http_application = None #The Tornado HTTP application code to be driven
    _http_server = None #The Tornado HTTP server instance
    
    def __init__(self, port, handlers, daemon=True):
        """
        Sets up and binds the HTTP server. All interfaces are glommed, though a port must be
        specified. The thread is run in daemon mode by default.
        
        `handlers` is a collection of tuples that connect a string or regular expression object that
        represents a path and a subclass of "BaseHandler".
        
        If it becomes necessary to bind to a specific interface, the following function will resolve
        names to IPs, which may (but hopefully will not) be necessary to traverse DNS entries that
        span subnets:
        #socket.gethostbyaddr('uguu.ca')
        #('web102.webfaction.com', [], ['174.120.139.132'])
        #Use this to resolve whatever IT puts in the config file; IPs and hostnames both resolve
        """
        threading.Thread.__init__(self)
        self.daemon = daemon
        self.name = "http"
        
        self._http_server = tornado.ioloop.IOLoop.instance()
        self._http_application = tornado.web.Application(handlers, log_function=(lambda x:''))
        self._http_application.listen(port)
        
        _logger.info("Configured HTTP server")
        
    def kill(self):
        """
        Ends execution of the HTTP server, allowing the thread to die.
        """
        _logger.info("HTTP server's kill-flag set")
        self._http_server.stop()
        
    def run(self):
        """
        Continuously accepts requests until killed; any exceptions that occur are logged.
        """
        _logger.info("Starting Tornado HTTP server engine...")
        self._http_server.start()
        _logger.info("Tornado HTTP server engine terminated")
        

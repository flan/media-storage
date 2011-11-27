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

import pymongo
import tornado.ioloop
import tornado.web

from config import CONFIG
import compression
import database
import mail
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
            _logger.debug("Request received from trusted host %(host)s" % {
             'host': host,
            })
            return _TrustLevel(True, True)
    if not record: #If `record` is omitted, the test is to see if the host is trusted globally
        return _TrustLevel(False, False)
        
    return _TrustLevel(
     record['keys']['read'] is None or keys and record['keys']['read'] == keys.get('read'),
     record['keys']['write'] is None or keys and record['keys']['write'] == keys.get('write'),
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
        _logger.debug("Extracting payload from nginx proxy structure...")
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
    def send_error(self, code, **kwargs):
        _logger.info("Responding to request from %(address)s with failure code %(code)i..." % {
         'address': self.request.remote_ip,
         'code': code,
        })
        tornado.web.RequestHandler.send_error(self, code, **kwargs)
        
    def post(self):
        """
        Handles an HTTP POST request.
        """
        _logger.debug("Received an HTTP POST request for '%(path)s' from %(address)s" % {
         'path': self.request.path,
         'address': self.request.remote_ip,
        })
        try:
            _logger.debug("Processing request...")
            output = self._post()
        except filesystem.Error as e:
            summary = "Filesystem error; exception details follow:\n" + traceback.format_exc()
            _logger.critical(summary)
            mail.send_alert(summary)
            raise
        except pymongo.errors.AutoReconnect:
            summary = "Database unavailable; exception details follow:\n" + traceback.format_exc()
            _logger.error(summary)
            mail.send_alert(summary)
            self.send_error(503)
        except Exception as e:
            _logger.error("Unknown error; exception details follow:\n" + traceback.format_exc())
            raise
        else:
            _logger.debug("Responding to request...")
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
            return
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
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
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
        if not trust.read:
            self.send_error(403)
            return
            
        del record['physical']['minRes']
        del record['keys']
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
            record = {
             '_id': header.get('uid') or uuid.uuid1().hex,
             'keys': self._build_key(header),
             'physical': {
              'family': header['physical'].get('family'),
              'ctime': current_time,
              'minRes': CONFIG.storage_minute_resolution,
              'atime': int(current_time),
              'format': self._build_format(header),
             },
             'policy': self._build_policy(header),
             'stats': {
              'accesses': 0,
             },
             'meta': header.get('meta') or {},
            }
        except KeyError as e:
            #log
            self.send_error(409)
            return
            
        target_compression = record['physical']['format'].get('comp')
        if target_compression and self.request.headers.get('Media-Storage-Compress-On-Server') == 'yes':
            compressor = getattr(compression, 'compress_' + target_compression)
            data = compressor(data)
            
        database.add_record(record)
        fs = state.get_filesystem(record['physical']['family'])
        fs.put(record, data)
        
        return {
         'uid': record['_id'],
         'keys': record['keys'],
        }
        
    def _build_key(self, header):
        header_key = header.get('keys')
        return {
         'read': header_key and header_key.get('read') or base64.urlsafe_b64encode(os.urandom(random.randint(10, 20)))[:-2],
         'write': header_key and header_key.get('write') or base64.urlsafe_b64encode(os.urandom(random.randint(10, 20)))[:-2],
        }
        
    def _build_format(self, header):
        format = {
         'mime': header['physical']['format']['mime'],
        }
        
        target_compression = header['physical']['format'].get('comp')
        if target_compression:
            format['comp'] = target_compression
            
        extension = header['physical']['format'].get('ext')
        if extension:
            format['ext'] = extension
            
        return format
        
    def _build_policy(self, header):
        policy = {
         'delete': {},
         'compress': {},
        }
        
        header_policy = header.get('policy')
        if header_policy:
            delete_policy = header_policy.get('delete')
            if delete_policy:
                policy['delete'].update(self._unpack_policy(delete_policy))
                
            compress_policy = header_policy.get('compress')
            if compress_policy:
                compress_format = compress_policy.get('comp')
                if compress_format in compression.SUPPORTED_FORMATS:
                    policy['compress']['comp'] = compress_format
                    policy['compress'].update(self._unpack_policy(compress_policy))
                else:
                    #log
                    pass
                    
        return policy
        
    def _unpack_policy(self, policy):
        new_policy = {}
        
        expiration = policy.get('fixed')
        if expiration:
            new_policy['fixed'] = int(time.time() + expiration)
            
        stale = policy.get('stale')
        if stale:
            new_policy['stale'] = int(stale)
            
        return new_policy
        
class UnlinkHandler(BaseHandler):
    def _get(self):
        request = _get_json(self.request.body)
        uid = request['uid']
        
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            return
            
        trust = _get_trust(record, request.get('keys'), self.request.remote_ip)
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
        

"""
Provides all resources needed for the HTTP interface.
"""
import base64
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

_logger = logging.getLogger("media_storage.http")

def _get_uid(path):
    return path[path.rfind('/') + 1:]
    
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
        Returns the received JSON-dict; override this to do useful things.
        """
        return {
         'timestamp': int(time.time()),
         'note': "This timestamp is in UTC; thanks for POSTing",
        }
        
#/get/<uid>
class GetHandler(BaseHandler):
    def _get(self):
        record = database.get_record(_get_uid(self.request.path))
        if not record:
            self.send_error(404)
            
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
            
#/describe/<uid>
class DescribeHandler(BaseHandler):
    def _get(self):
        record = database.get_record(_get_uid(self.request.path))
        if not record:
            self.send_error(404)
            
        self.write(record)
        self.finish()
        
#/query
class QueryHandler(BaseHandler):
    def _post(self):
        pass
        
#/store
class StoreHandler(BaseHandler):
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
                
            record = {
             '_id': header.get('uid') or uuid.uuid1().hex,
             'key': header.get('key') or base64.urlsafe_b64encode(os.urandom(random.randint(15, 25)))[:-2],
             'physical': {
              'family': header['physical'].get('family'),
              'ctime': current_time,
              'minRes': CONFIG.minute_resolution,
              'atime': int(current_time),
              'format': format,
             },
             'policy': header.get('policy') or {},
             'stats': {
              'accesses': 0,
             },
             'meta': header.get('meta') or {},
            }
        except KeyError as e:
            #log
            self.send_error(409)
            print e
        else:
            print record
            print repr(data.read())
            database.put_record(record)
            fs = state.get_filesystem(record['physical']['family'])
            fs.put(record, data)
            
#/unlink/<uid>
class UnlinkHandler(BaseHandler):
    def _get(self):
        uid = _get_uid(self.request.path)
        record = database.get_record(uid)
        if not record:
            self.send_error(404)
            
        fs = state.get_filesystem(record['physical']['family'])
        try:
            fs.unlink(record)
        except filesystem.FileNotFoundError as e:
            self.send_error(404)
        else:
            database.drop_record(uid)
            
            
            
            
            
            
            
"""
Provides a general-purpose JSON-aware HTTP server that receives data using POST.

The server does nothing useful by default, but may be extended with custom handlers, on a per-path
basis, as in the following example::

 class Handler(rest_json.reception.BaseHandler):
    def _get(self):
        return {
         'hello': 'I am a JSON-serialisable object',
        }
        
    def _post(self, request):
        return {
         'hi': 'I am also a JSON-serialisable object, but I have the deserialised JSON object passed with the POST request to play with',
        }
        
 server = HTTPService(port=1234, [
  (r'/', Handler)
 ], daemon=False)
 server.start()
"""




        
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
        

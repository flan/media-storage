"""
Provides all resources needed for the HTTP interface.
"""
import json

import compression
import database
import filesystem
import state

_CHUNK_SIZE = 16 * 1024 #Write 16k at a time.

#uid = self.request.path[request.path.rfind('/') + 1:]

#/get/<uid>
class GetHandler(GetHandler):
    def _get(self, uid):
        record = database.get_record(uid)
        if not record:
            #404
            
        filesystem = state.get_filesystem(record['physical']['family'])
        try:
            data = filesystem.get(record)
        except filesystem.FileNotFoundError as e:
            #log
            #404
        else:
            applied_compression = record['physical']['format'].get('comp')
            supported_compressions = (c.strip() for c in (self.request.headers.get('Ivr-Supported-Compression') or '').split(';'))
            if applied_compression and not applied_compression in supported_compressions: #Must be decompressed first
                #log
                decompressor = getattr(compression, 'decompress_' + applied_compression)
                data = decompressor(data)
                applied_compression = None
                
            self.headers['Content-Type'] = record['physical']['format']['mime']
            self.headers['Content-Length'] = str(filesystem.file_size(record))
            while True:
                chunk = data.read(_CHUNK_SIZE)
                if chunk:
                    self.write(chunk)
                    self.flush()
                else:
                    break
            self.finish()
            
#/describe/<uid>
def DescribeHandler(GetHandler):
    def _get(self, uid):
        record = database.get_record(uid)
        if not record:
            #404
            
        self.write(record)
        self.finish()
        
#/query
def QueryHandler(JSONHandler):
    def _post(self, request):
        pass
        
#/store
def StoreHandler(HybridHandler):
    def _post(self, request):
        pass
        
#/unlink
def UnlinkHandler(GetHandler):
    def _get(self, uid):
        record = database.get_record(uid)
        if not record:
            #404
            
        filesystem = state.get_filesystem(record['physical']['family'])
        try:
            filesystem.unlink(record)
        except filesystem.FileNotFoundError as e:
            #404
        else:
            database.drop_record(record['_uid'])
            
            
            
            
            
            
            
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
__author__ = 'Neil Tallim'

import json
import logging
import threading
import time
import traceback
import zlib

import tornado.ioloop
import tornado.web

_COMPRESSION_LIMIT = 32 * 1024 #Anything larger than 32k gets compressed transparently

_logger = logging.getLogger("rest_json.reception")

class BaseHandler(tornado.web.RequestHandler):
    """
    A generalised request-handler for inbound communication; it abstracts away most of the
    complexity of REST-JSON, allowing you to override the '_post(<json-request:dict>)' or '_get()'
    methods in a subclass, then bind it to a request path.
    
    Responds with one of the following codes::
    
    - 200 if everything went well
    - 409 if the request made no sense
    - 500 if an internal exception happened
    
    The body for a 200 response depends on the API definition for the requested operation. For
    everything else, the JSON response will always contain a 'message' value, which carries a
    human-readable string, and possibly other values, with meanings varying depending on request.
    """
    def get(self):
        """
        Handles an HTTP GET request.
        """
        _logger.debug("Received an HTTP GET request for '%(path)s'" % {
         'path': self.request.path,
        })
        
        _logger.debug('Determining servicability and preparing response...')
        body = None
        try:
            body = self._get()
        except Exception as e:
            body = {
             'message': "An error occurred while processing the request; full details are available in the server's logs",
            }
            _logger.error("Unable to serve response to HTTP request; exception details follow\n" + traceback.format_exc())
            self.write_error(500, body=body)
        else:
            self._write_body(body)
            
        self.finish()
        
    def post(self):
        """
        Extracts the payload and coerces it to JSON for an HTTP POST request.
        """
        _logger.debug("Received an HTTP POST request for '%(path)s'" % {
         'path': self.request.path,
        })
        
        _logger.debug('Determining servicability and preparing response...')
        body = None
        try:
            request_body = self.request.body
            if self.request.headers.get('Transfer-Encoding') == 'gzip':
                request_body = json.loads(zlib.decompress(request_body))
            else:
                request_body = json.loads(request_body)
        except Exception as e:
            body = {
             'message': "The request received contained no parsable JSON data or specified an invalid Content-Length",
            }
            _logger.warn(body['message'])
            self.write_error(409, body=body)
        else:
            try:
                body = self._post(request_body)
            except Exception as e:
                body = {
                 'message': "An error occurred while processing the request; full details are available in the server's logs",
                }
                _logger.error("Unable to serve response to HTTP request; exception details follow\n" + traceback.format_exc())
                self.write_error(500, body=body)
            else:
                self._write_body(body)
                
        self.finish()
        
    def write_error(self, code, **kwargs):
        """
        Passes through 'body' to the write function, to facilitate informative response messages.
        """
        self.set_status(code)
        self._write_body(kwargs.get('body'))
        
    def _write_body(self, body):
        """
        Writes the JSON-dictionary body to the HTTP response and finishes the request.
        """
        _logger.debug("Sending response...")
        body = json.dumps(body)
        if 'gzip' in (self.request.headers.get('Accept-Encoding') or ''): #Serialise the data first to allow for compression
            if len(body) >= _COMPRESSION_LIMIT: #Compress the data
                body = zlib.compress(body)
                self.set_header('Transfer-Encoding', 'gzip')
        self.write(body)
        self.set_header('Content-Type', 'application/json')
        self.set_header('Connection', 'close')
        _logger.debug("Response sent")
        
    def _get(self):
        """
        Returns the current time; override this to do useful things.
        """
        return {
         'current-time': int(time.mktime(time.gmtime())),
         'note': "This timestamp is in UTC",
        }
        
    def _post(self, request):
        """
        Returns the received JSON-dict; override this to do useful things.
        """
        return request
        
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
        self.name = "rest_json-http"
        
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
        

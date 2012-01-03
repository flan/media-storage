import base64
import BaseHTTPServer
import json
import logging
import os
import SocketServer
import threading
import uuid

from config import CONFIG
import filesystem

_logger = logging.getLogger('media_storage.http')

class _Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def address_string(self):
        """
        Disable reverse-lookups.
        """
        return self.client_address[0]
        
    def log_message(self):
        """
        Logging happens internally.
        """
        
    def do_POST(self):
        if not self.path == '/put':
            _logger.warn("Request received for unsupported path %(path)s from %(addr)s" % {
             'path': self.path,
             'addr': self.address_string(),
            })
            self.send_response(404)
            self.end_headers()
            return
            
        try:
            _logger.info("Storage request received from %(addr)s" % {
             'addr': self.address_string(),
            })
            
            request = json.loads(self.rfile.read())
            
            record = {
             'uid': request.get('uid') or uuid.uuid1().hex,
             'keys': self._build_keys(request),
             'physical': request['family'],
             'policy': request['policy'],
             'meta': request['meta'],
            }
            
            _logger.info("Writing files for '%(uid)s'..." % {
             'uid': record['uid'],
            })
            filesystem.add_entity(request['proxy']['server']['host'], request['proxy']['server']['port'], request['data'], record)
            
            _logger.info("Stored '%(uid)s'" % {
             'uid': record['uid'],
            })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
             'uid': record['uid'],
             'keys': record['keys'],
            }))
        except Exception as e:
            _logger.error("An unhandled exception occurred; strack trace follows:\n" + traceback.format_exc())
            self.send_response(500)
            self.end_headers()
            
    def _build_keys(self, request):
        keys = request.get('keys')
        return {
         'read': keys and keys.get('read') or base64.urlsafe_b64encode(os.urandom(random.randint(5, 10)))[:-2],
         'write': keys and keys.get('write') or base64.urlsafe_b64encode(os.urandom(random.randint(5, 10)))[:-2],
        }
        
class _ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """
    Spawns new threads to handle inbound HTTP requests.
    """
    
class HTTPService(threading.Thread):
    """
    A threaded handler for HTTP requests.
    
    Starts with `start()` and executes until `kill()` is invoked.
    """
    _http_server = None #The HTTP server instance
    
    def __init__(self, daemon=True):
        """
        Sets up and binds the HTTP server on the localhost interface. The thread is run in daemon
        mode by default.
        """
        threading.Thread.__init__(self)
        self.daemon = daemon
        self.name = "http"
        
        _logger.info("Configuring HTTP server on localhost, port %(port)i..." % {
         'port': CONFIG.http_port,
        })
        self._http_server = _ThreadedHTTPServer(('localhost', CONFIG.http_port), _Handler)
        _logger.info("Configured HTTP server")
        
    def kill(self):
        """
        Ends execution of the HTTP server, allowing the thread to die.
        """
        _logger.info("HTTP server's kill-flag set")
        self._http_server.shutdown()
        
    def run(self):
        """
        Continuously accepts requests until killed; any exceptions that occur are logged.
        """
        _logger.info("Starting HTTP server engine...")
        self._http_server.serve_forever()
        _logger.info("HTTP server engine terminated")
        

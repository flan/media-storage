import BaseHTTPServer
import json
import SocketServer
import threading

from config import CONFIG
import cache

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
        if path == '/get':
            self._get()
        elif path == '/describe':
            self._describe()
        else:
            _logger.warn("Request received for unsupported path %(path)s from %(addr)s" % {
             'path': self.path,
             'addr': self.address_string(),
            })
            self.send_response(404)
            self.end_headers()
            
    def _get(self):
        _logger.debug("Retrieval request received from %(addr)s" % {
         'addr': self.self.address_string(),
        })
        request = json.loads(self.rfile.read())
        _logger.info("Attempting to serve request for content of '%(uid)s' from %(addr)s..." % {
         'uid': request['uid'],
         'addr': self.self.address_string(),
        })
        
        content = cache.get(
         request['proxy']['server']['host'], request['proxy']['server']['port'],
         request['uid'], request['keys']['read']
        )
        
        if not content:
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-Type', content[0])
            self.end_headers()
            self.wfile.write(content[1])
            
    def _describe(self):
        _logger.debug("Description request received from %(addr)s" % {
         'addr': self.self.address_string(),
        })
        request = json.loads(self.rfile.read())
        
        
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(_____meta_____))
        
class _ThreadedHTTPServer(ThreadingMixIn.ThreadingMixIn, BaseHTTPServer.HTTPServer):
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
        

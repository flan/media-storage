import BaseHTTPServer
import json
import SocketServer
import threading

from config import CONFIG
import filesystem

class _Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        if not path == '/put':
            self.send_response(404)
            self.end_headers()
            return
            
        #Generate UID and keys
        #Copy file
        #Write meta
        #Add record to queue
        
        self.send_response(200)
        #Set content type
        self.end_headers()
        self.wfile.write(json.dumps(_____uid/keys_____))
        
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
        

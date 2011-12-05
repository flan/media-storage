"""
Provides an implementation for the caching proxy client.
"""
import json

import interfaces
import compression

class CachingProxyClient(interfaces.RetrievalConstruct):
    #When a proxy first gets a get or describe for an uncached record, it performs both actions,
    #since it needs meta anyway, with the describe coming first. If there is no cache metadata,
    #the get is not performed, unless a get was explicitly requested.
    
    #Cached content must be separated into directories based on server name: whee.uguu.ca_8080/
    
    def __init__(self, server_host, server_port, proxy_port):
        self._server_host = server_host
        self._server_port = server_port
        self._proxy = 'http://localhost:%(port)i/' % {
         'port': proxy_port,
        }
        
    def get(self, uid, read_key, output_file=None, decompress_on_server=False, timeout=5.0):
        """
        Retrieves the requested data from the cache, returning its MIME and the decompressed
        content as an open filehandle on the cached file in a tuple.
        
        `uid` and `read_key` are used to access the requested data.
        
        `output_file` is ignored because the actual file instance is returned.
        
        `decompress_on_server` is ignored, since the caching proxy always tries to do local
        decompression in the middle.
        
        `timeout` is the number of seconds to allow for retrieval to complete. Defaults to 5.0s.
        """
        request = common.assemble_request(self._proxy + common.SERVER_GET, {
         'uid': uid,
         'keys': {
          'read': read_key,
         },
         'proxy': {
          'server': {
           'host': self._server_host,
           'port': self._server_port,
          },
         },
        })
        (properties, response) = common.send_request(request, timeout=timeout)
        response = json.loads(response)
        return (properties.get(common.PROPERTY_CONTENT_TYPE), open(response['filePath'], 'rb'))
        
    def describe(self, uid, read_key, timeout=2.5):
        """
        Retrieves the requested record from the server as a dictionary.
        
        `uid` and `read_key` are used to access the requested data.
        
        `timeout` is the number of seconds to allow for retrieval to complete. Defaults to 2.5s.
        """
        request = common.assemble_request(self._proxy + common.SERVER_DESCRIBE, {
         'uid': uid,
         'keys': {
          'read': read_key,
         },
         'proxy': {
          'server': {
           'host': self._server_host,
           'port': self._server_port,
          },
         },
        })
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        

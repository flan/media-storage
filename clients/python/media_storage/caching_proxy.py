"""
media_storage.caching_proxy
===========================

Provides an implementation for a client that works with a local caching proxy.

Usage
-----

This module is not meant to be used externally; relevant objects are exported
to the package level.

Legal
-----

This file is part of the LGPLed Python client of the media-storage project.
This package is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and
GNU Lesser General Public License along with this program. If not, see
<http://www.gnu.org/licenses/>.
 
(C) Neil Tallim, 2011
"""
import json

import interfaces
import common
import compression
import tempfile

_TEMPFILE_SIZE = 256 * 1024 #Keep reasonable-sized tempfiles in memory

class CachingProxyClient(interfaces.RetrievalConstruct):
    """
    Implements the retrieval mechanisms of the client specification such that all interaction takes
    place with a server running on the same host as the client, with that server being responsbible
    for maintaining a local cache of requested data, to reduce overall network load and increase
    response times for high-demand resources.
    
    All operations performed by an instance of this class are atomic and instantaneous, but they
    incur some additional local server load, meaning that it is a poor choice for data that is
    accessed infrequently, but a good choice for templates and attachments that are sent out
    repeatedly during campaigns.
    """
    def __init__(self, server_host, server_port, proxy_port):
        """
        `server_host` and `server_port` indicate the address of the server to be used for
        operations; the port must be an integer and the host may be an IP or name.
        
        `proxy_port` is the port on which the caching proxy is listening on the 'localhost'
        interface.
        """
        self._server_host = server_host
        self._server_port = server_port
        self._proxy = 'http://localhost:%(port)i/' % {
         'port': proxy_port,
        }
        
    def get(self, uid, read_key, output_file=None, decompress_on_server=False, timeout=5.0):
        """
        Retrieves the requested data from the local proxy, returning its MIME and the decompressed
        content as an open filehandle in a tuple.
        
        `output_file` is the path of the file to which the response is written; an anonymous
        tempfile is used by default. If supplied, the caller is responsble for cleaning it up.
        
        `decompress_on_server` is ignored; the caching proxy is responsible for that.
        
        `timeout` defaults to 5.0s.
        
        All other arguments are the same as in ``media_storage.interfaces.RetrievalConstruct.get``.
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
        
        if not output_file:
            output = tempfile.SpooledTemporaryFile(_TEMPFILE_SIZE)
        else:
            output = open(output_file, 'wb')
        output.write(response)
        output.seek(0)
        
        return (properties.get(common.PROPERTY_CONTENT_TYPE), output)
        
    def describe(self, uid, read_key, timeout=2.5):
        """
        Retrieves the requested record from the local proxy as a dictionary.
        
        `timeout` defaults to 2.5s.
        
        All other arguments are the same as in
        ``media_storage.interfaces.ControlConstruct.describe``.
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
        

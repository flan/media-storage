"""
media_storage.storage_proxy
===========================

Provides an implementation for a client that works with a local deferred
storage proxy.

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
"""
Provides an implementation for the proxy client.
"""
import json

import interfaces
import common
import compression

class StorageProxyClient(interfaces.StorageConstruct):
    """
    Implements the storage mechanisms of the client specification such that all interaction takes
    place with a server running on the same host as the client, with that server being responsbible
    for buffering and ensuring eventual delivery of uploaded content, to reduce potential damages
    caused by network disruptions.
    
    All operations performed by an instance of this class are deferred, making it a good choice for
    time-independent operations where the caller cannot or should not handle delivery failures, but
    the wrong choice if the caller must guarantee that data is available immediately.
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
        
    def ping(self, timeout=1.0):
        """
        Indicates whether the proxy is online or not, raising an exception in case of failure.
        
        `timeout` is the number of seconds to allow for pinging to complete, defaulting to 1.0s.
        """
        request = common.assemble_request(self._proxy + common.SERVER_PING, {})
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
    def put(self, data, mime, family=None,
     comp=compression.COMPRESS_NONE, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None,
     timeout=3.0
    ):
        """
        Stores data in the proxy's buffers, immediately returning a dictionary containing the keys
        'uid', which points to the eventual UID of the stored data, and 'keys', which is another
        dictionary containing 'read' and 'write', the keys needed to perform either type of action
        on the stored data.
        
        It is important to note that the data is NOT actually stored when this pointer is returned,
        but rather that the pointer will be valid at some point in the future (typically very soon,
        but not within a predictable timeframe).
        
        `data` is a string containing the local filesystem path of the data to store and `mime` is
        the MIME-type of the data.
        
        `timeout` defaults to 3.0s, but should be adjusted depending on your server's performance.
        
        All other arguments are the same as in ``media_storage.interfaces.ControlConstruct.put``.
        """
        description = {
         'uid': uid,
         'keys': keys,
         'physical': {
          'family': family,
          'format': {
           'mime': mime,
           'comp': comp,
          },
         },
         'policy': {
          'delete': deletion_policy,
          'compress': compression_policy,
         },
         'meta': meta,
         'proxy': {
          'server': {
           'host': self._server_host,
           'port': self._server_port,
          },
          'data': data,
         },
        }
        
        request = common.assemble_request(self._proxy + common.SERVER_PUT, description)
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        

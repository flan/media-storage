"""
media_storage.client
====================

Provides an implementation for the core client, which speaks directly with
servers.

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
import StringIO
import tempfile
import types

import common
import compression
import interfaces

_TEMPFILE_SIZE = 256 * 1024 #Keep reasonable-sized tempfiles in memory

class Client(interfaces.ControlConstruct):
    """
    Defines a client interface for communicating directly with a server.
    
    All operations performed by an instance of this class are atomic and instantaneous, making it
    the right choice for time-dependent operations, but the wrong choice if the caller cannot handle
    failure scenarios.
    """
    _server = None #The server to which requests are sent
    
    def __init__(self, server_host, server_port):
        """
        `server_host` and `server_port` indicate the address of the server to be used for
        operations; the port must be an integer and the host may be an IP or name.
        """
        self._server = 'http://%(host)s:%(port)i/' % {
         'host': server_host,
         'port': server_port,
        }
        
    def status(self, timeout=2.5):
        """
        Yields a dictionary of load data from the server::
        
            'process': {
             'cpu': {'percent': 0.1,},
             'memory': {'percent': 1.2, 'rss': 8220392,},
             'threads': 4,
            },
            'system': {
             'load': {'t1': 0.2, 't5': 0.5, 't15': 0.1,},
            }
            
        `timeout` is the number of seconds to allow for retrieval to complete, defaulting to 2.5s.
        """
        request = common.assemble_request(self._server + common.SERVER_STATUS, {})
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
    def ping(self, timeout=1.0):
        """
        Indicates whether the server is online or not, raising an exception in case of failure.
        
        `timeout` is the number of seconds to allow for pinging to complete, defaulting to 1.0s.
        """
        request = common.assemble_request(self._server + common.SERVER_PING, {})
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
    def list_families(self, timeout=2.5):
        """
        Enumerates all families currently defined on the server, returning a sorted list of strings.
        
        `timeout` is the number of seconds to allow for retrieval to complete, defaulting to 2.5s.
        """
        request = common.assemble_request(self._server + common.SERVER_LIST_FAMILIES, {})
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)['families']
        
    def put(self, data, mime, family=None,
     comp=compression.COMPRESS_NONE, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None,
     timeout=10.0
    ):
        """
        Stores data on a server, returning a dictionary containing the keys 'uid', which points to
        the UID of the stored data, and 'keys', which is another dictionary containing 'read' and
        'write', the keys needed to perform either type of action on the stored data.
        
        `data` is a string or file-like object containing the payload to be stored and `mime` is the
        MIME-type of the data.
        
        `timeout` defaults to 10.0s, but should be adjusted depending on your needs.
        
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
        }
        
        headers = {}
        if comp:
            if not compress_on_server:
                try:
                    if type(data) in types.StringTypes: #The compressors expect file-like objects
                        data = StringIO.StringIO(data)
                    data = compression.get_compressor(comp)(data)
                except ValueError:
                    headers[common.HEADER_COMPRESS_ON_SERVER] = common.HEADER_COMPRESS_ON_SERVER_TRUE
            else:
                headers[common.HEADER_COMPRESS_ON_SERVER] = common.HEADER_COMPRESS_ON_SERVER_TRUE
                
        request = common.assemble_request(self._server + common.SERVER_PUT, description, headers=headers, data=data)
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
    def get(self, uid, read_key, output_file=None, decompress_on_server=False, timeout=5.0):
        """
        Retrieves the requested data from the server, returning its MIME and the decompressed
        content as a file-like object (optionally that supplied as `output_file`) in a tuple; the
        file-like object has a ``length`` parameter that contains its length in bytes.
        
        `output_file` is an optional file-like object to which data should be written (a spooled
        tempfile is used by default).
        
        `timeout` defaults to 5.0s.
        
        All other arguments are the same as in ``media_storage.interfaces.ControlConstruct.get``.
        """
        headers = {}
        if not decompress_on_server: #Tell the server what the client supports
            headers[common.HEADER_SUPPORTED_COMPRESSION] = common.HEADER_SUPPORTED_COMPRESSION_DELIMITER.join(compression.SUPPORTED_FORMATS)
            
        request = common.assemble_request(self._server + common.SERVER_GET, {
         'uid': uid,
         'keys': {
          'read': read_key,
         },
        }, headers=headers)
        if not output_file:
            output = tempfile.SpooledTemporaryFile(_TEMPFILE_SIZE)
        else:
            output = output_file
        properties = common.send_request(request, output=output, timeout=timeout)
        
        length = properties.get(common.PROPERTY_CONTENT_LENGTH)
        if properties.get(common.PROPERTY_APPLIED_COMPRESSION):
            output = compression.get_decompressor(properties.get(common.PROPERTY_APPLIED_COMPRESSION))(output)
            if output_file: #The decompression process returns a tempfile
                output_file.seek(0)
                output_file.truncate()
                length = common.transfer_data(output, output_file)
                output = output_file
        
        output.length = length
        return (properties.get(common.PROPERTY_CONTENT_TYPE), output)
        
    def describe(self, uid, read_key, timeout=2.5):
        """
        Retrieves the requested record from the server as a dictionary.
        
        `timeout` defaults to 2.5s.
        
        All other arguments are the same as in
        ``media_storage.interfaces.ControlConstruct.describe``.
        """
        request = common.assemble_request(self._server + common.SERVER_DESCRIBE, {
         'uid': uid,
         'keys': {
          'read': read_key,
         },
        })
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
    def unlink(self, uid, write_key, timeout=2.5):
        """
        Unlinks the identified data on the server.
        
        `timeout` defaults to 2.5s.
        
        All other arguments are the same as in ``media_storage.interfaces.ControlConstruct.unlink``.
        """
        request = common.assemble_request(self._server + common.SERVER_UNLINK, {
         'uid': uid,
         'keys': {
          'write': write_key,
         },
        })
        common.send_request(request, timeout=timeout)
        
    def update(self, uid, write_key,
     new={}, removed=(),
     deletion_policy=None, compression_policy=None,
     timeout=2.5
    ):
        """
        Updates attributes of an existing record on a server.
        
        `timeout` defaults to 2.5s.
        
        All other arguments are the same as in ``media_storage.interfaces.ControlConstruct.update``.
        """
        request = common.assemble_request(self._server + common.SERVER_UPDATE, {
         'uid': uid,
         'keys': {
          'write': write_key,
         },
         'policy': {
          'delete': deletion_policy,
          'compress': compression_policy,
         },
         'meta': {
          'new': new,
          'removed': removed,
         },
        })
        common.send_request(request, timeout=timeout)
        
    def query(self, query, timeout=5.0):
        """
        Returns a list of matching records, up to the server's limit.
        
        `timeout` defaults to 5.0s.
        
        All other arguments are the same as in ``media_storage.interfaces.ControlConstruct.query``.
        """
        request = common.assemble_request(self._server + common.SERVER_QUERY, query.to_dict())
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)['records']
        

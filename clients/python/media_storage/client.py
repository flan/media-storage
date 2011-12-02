"""
Provides an implementation for the main client.
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
    _server = None #The server to which requests are sent
    
    def __init__(self, server):
        self._server = server
        
    def put(self, data, mime, family=None,
     extension=None, comp=compression.COMPRESS_NONE, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None,
     timeout=10.0
    ):
        """
        Stores data on a server.
        
        `data` is a string or file-like object containing the payload to be stored and `mime` is the
        MIME-type of the data.
        
        `family`, which is optional (defaulting to `None`, meaning "generic"), can be used to store
        data in different filesystems or, more simply, as a means of logically separating data in
        queries. 
        
        `extension` is an optional extension to use when suggesting a filename on retrieval;
        `comp` is the type of compression to be applied, as one of the compression type
        constants (defaulting to uncompressed); `compress_on_server` indicates whether compression
        should happen locally (recommended in most cases) or on the server (which will require an
        appropriate timeout value).
        
        `deletion_policy` may either be `None`, which means the file is never deleted (default) or
        a dictionary containing one or both of the following:
         - 'fixed': The number of seconds to retain the file from the time it is uploaded
         - 'stale': The number of seconds that must elapse after the file was last downloaded to
                    qualify it for deletion
                    
        `compression_policy` works the same as `deletion_policy`, only with one extra element:
         - 'comp': Any of the compression type constants, except for none; this will cause the data
                   to be (re)compressed in that format when either condition is met.
        
        `meta` is a dictionary (or `None`) containing any metadata to be used to identify the
        uploaded content through querying. All scalar value-types are supported.
        
        If not implementing a proxy, do not pass anything for `uid` or otherwise pick something that
        has no chance of colliding with a UUID(1).
        
        In general, you should not need to specify anything for `keys`, but if you have a homogenous
        or anonymous access policy, it is a dictionary containing the elements 'read' and 'write',
        both strings or `None`, with `None` granting anonymous access to the corresponding facet.
        Either element may be omitted to have it generated by the server.
        
        `timeout` defaults to 10.0s, but should be adjusted depending on your needs.
        
        The value returned is a dictionary containing the keys 'uid', which points to the UID of the
        stored data, and 'keys', which is another dictionary containing 'read' and 'write', the
        keys needed to perform either type of action on the stored data.
        """
        description = {
         'uid': uid,
         'keys': keys,
         'physical': {
          'family': family,
          'format': {
           'mime': mime,
           'ext': extension,
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
        content as a file-like object (optionally that supplied as `output_file`) in a tuple.
        
        `uid` and `read_key` are used to access the requested data.
        
        `output_file` is an optional file to which data should be written (a tempfile is used by
        default).
        
        `decompress_on_server` ensures that the server will handle decompression, though this also
        happens if the client doesn't support the compression in use. This should be left off, which
        is the default, unless necessary.
        
        `timeout` is the number of seconds to allow for retrieval to complete; if decompressing, it
        should be increased accordingly. Defaults to 5.0s.
        """
        headers = {}
        if not decompress_on_server: #Tell the server what the client supports
            headers[HEADER_SUPPORTED_COMPRESSION] = HEADER_SUPPORTED_COMPRESSION_DELIMITER.join(compression.SUPPORTED_FORMATS)
            
        request = common.assemble_request(self._server + common.SERVER_GET, {
         'uid': uid,
         'keys': {
          'read': read_key,
         },
        })
        if not output_file:
            output = tempfile.SpooledTemporaryFile(_TEMPFILE_SIZE)
        else:
            output = output_file
        properties = common.send_request(request, output=output, timeout=timeout)
        
        if properties.get(PROPERTY_APPLIED_COMPRESION):
            output = compression.get_decompressor(properties.get(PROPERTY_APPLIED_COMPRESION))(output)
            if output_file: #The decompression process returns a tempfile
                output_file.seek(0)
                output_file.truncate()
                common.transfer_data(output, output_file)
                output = output_file
                
        return (properties.get(common.PROPERTY_CONTENT_TYPE), output)
        
    def describe(self, uid, read_key, timeout=2.5):
        """
        Retrieves the requested record from the server as a dictionary.
        
        `uid` and `read_key` are used to access the requested data.
        
        `timeout` is the number of seconds to allow for retrieval to complete. Defaults to 2.5s.
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
        
        `uid` and `write_key` are used to access the requested data.
        
        `timeout` is the number of seconds to allow for unlinking to complete. Defaults to 2.5s.
        """
        request = common.assemble_request(self._server + common.SERVER_UNLINK, {
         'uid': uid,
         'keys': {
          'write': write_key,
         },
        })
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
    def update(self, uid, write_key,
     new={}, removed=(),
     deletion_policy=None, compression_policy=None,
     timeout=2.5
    ):
        """
        Updates attributes of an existing record on a server.
        
        `uid` and `write_key` are used to access the requested data.
        
        `new` is a dictionary of meta-data that will be used to update (add and replace) existing
        meta-data. `removed` is a collection of meta-data keys to be dropped. By default, both are
        empty.
        
        `deletion_policy` is either `None`, which effects no change (the default) or a dictionary,
        of the same form as in `put()`, that replaces the current policy. `compression_policy` is
        the same.
        
        `timeout` defaults to 2.5s, but should be adjusted depending on your needs.
        """
        update = {
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
        }
        
        request = common.assemble_request(self._server + common.SERVER_UPDATE, update)
        (properties, response) = common.send_request(request, timeout=timeout)
        
    def query(self, query, timeout=5.0):
        """
        Given a QueryStruct as `query`, a list of all matching records, up to the server's limit,
        is returned as a list of records.
        
        `timeout` defaults to 5.0s, but should be adjusted if the server is known to be slow to
        respond.
        """
        request = common.assemble_request(self._server + common.SERVER_QUERY, query.to_dict())
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)['records']
        

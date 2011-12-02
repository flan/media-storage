"""
Provides an implementation for the proxy client.
"""
import json

import interfaces

class StorageProxyClient(interfaces.StorageConstruct):
    def __init__(self, server, proxy):
        self._server = server
        self._proxy = proxy
        
    def put(self, data, mime, family=None,
     extension=None, comp=compression.COMPRESS_NONE, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None,
     timeout=3.0
    ):
        """
        Hands data to a local proxy for deferred delivery to a server.
        
        `data` is a string containing the local filesystem path of the data to store and `mime` is
        the MIME-type of the data.
        
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
        
        `timeout` defaults to 3.0s, but should be adjusted depending on your host's performance.
        
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
         'proxy': {
          'server': self._server,
          'data': data,
         },
        }
        
        request = common.assemble_request(self._proxy + common.SERVER_PUT, description)
        (properties, response) = common.send_request(request, timeout=timeout)
        return json.loads(response)
        
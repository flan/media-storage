"""
Provides an implementation for the main client.
"""
import common
import interfaces

class Client(interfaces.ControlConstruct):
    def put(self, data, mime, family=None,
     extension=None, compression=None, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None
    ):
        (data, checksum) = common.process_file(data)
        description = {
         'uid': uid,
         'keys': keys,
         'physical': {
          'family': family,
          'checksum': checksum,
          'format': {
           'mime': mime,
           'ext': extension,
           'comp': compression,
          },
         },
         'policy': {
          'delete': deletion_policy,
          'compress': compression_policy,
         },
         'meta': meta,
        }
        

        raise NotImplementedError("put() must be overridden in child classes")
        
    def get(self, uid, read_key):
        raise NotImplementedError("get() must be overridden in child classes")
        
    def describe(self, uid, read_key):
        raise NotImplementedError("describe() must be overridden in child classes")
        
    def delete(self, uid, write_key):
        raise NotImplementedError("delete() must be overridden in child classes")
        
    def query(self):
        raise NotImplementedError("query() must be overridden in child classes")
        
    def update(self, uid, write_key, new={}, removed=(), deletion_policy=None, compression_policy=None):
        raise NotImplementedError("update_meta() must be overridden in child classes")
        

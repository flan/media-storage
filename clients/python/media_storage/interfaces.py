"""
Defines interfaces that implementing classes must fulfill.
"""
from abc import ABCMeta, abstractmethod

class StorageConstruct(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def put((self, data, mime, family=None,
     extension=None, comp=compression.COMPRESS_NONE, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None,
     timeout=10.0
    ):
        """
        If either policy is a dictionary, it value replaces that on the server; an empty dictionary
        disables the policy. None effects no change.
        """
        """
        Full implementations are possible. @abstractmethod just means that the method must be
        present in any derived classes, whether inherited or otherwise.
        """
        raise NotImplementedError("put() must be overridden in child classes")
        
class RetrievalConstruct(object):
    __metaclass__ = ABCMeta
    
    #describe will be implemented as a pass-through on the proxy
    
    @abstractmethod
    def get(self, uid, read_key, output_file=None, decompress_on_server=False, timeout=5.0):
        raise NotImplementedError("get() must be overridden in child classes")
        
    @abstractmethod
    def describe(self, uid, read_key, timeout=2.5):
        raise NotImplementedError("describe() must be overridden in child classes")
        
class ControlConstruct(StorageConstruct, RetrievalConstruct):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def unlink(self, uid, write_key, timeout=2.5):
        raise NotImplementedError("delete() must be overridden in child classes")
        
    @abstractmethod
    def update(self, uid, write_key,
     new={}, removed=(),
     deletion_policy=None, compression_policy=None,
     timeout=2.5
    ):
        raise NotImplementedError("update_meta() must be overridden in child classes")
        
    @abstractmethod
    def query(self, query, timeout=5.0):
        raise NotImplementedError("query() must be overridden in child classes")
        
class QueryStruct(object):
    """
    The structure used to issue queries against a server.
    
    All attributes are meant to be set publically, though `meta` is a dictionary and should be
    treated as such, being populated with keys to check and value to match on, of appropriate types.
    
    To perform non-matching queries on metadata, the following filters may be used:
     - ':range:<min>:<max>' : range queries over numeric types, inclusive on both ends
     - ':lte:<number>'/':gte:<number>' : relative queries over numeric types
     - ':re:<pcre>'/':re.i:<pcre>' : PCRE regular expression, with the second form being
       case-insensitive
     - ':like:<pattern>' : behaves like SQL 'LIKE', with '%' as wildcards
     - ':ilike:<pattern>' : behaves like SQL 'ILIKE', with '%' as wildcards
     - '::<whatever>' : Ignores the first colon and avoids parsing, in case a value actually starts
       with a ':<filter>:' structure
       
    In addition to `meta`, the following fields are defined:
     - `ctime_min`/`ctime_max` : if either is set, it serves as an <=/>= check against ctime
     - `atime_min`/`atime_max` : if either is set, it serves as an <=/>= check against atime
     - `accesses_min`/`accesses_max` : if either is set, it serves as an <=/>= check against
       accesses
     - `family` : if set, performs an explicit match against family
     - `mime` : if set, if a '/' is present, performs an explicit match against MIME; otherwise,
       performs a match against the super-type of MIME
    """
    ctime_min = None
    ctime_max = None
    atime_min = None
    atime_max = None
    accesses_min = None
    accesses_max = None
    family = None
    mime = None
    meta = None
    
    def __init__(self):
        self.meta = {}
        
    def to_dict(self):
        return {
         'ctime': {
          'min': self.ctime_min,
          'max': self.ctime_max,
         },
         'atime': {
          'min': self.atime_min,
          'max': self.atime_max,
         },
         'accesses': {
          'min': self.accesses_min,
          'max': self.accesses_max,
         },
         'family': self.family,
         'mime': self.mime,
         'meta': self.meta,
        }
        

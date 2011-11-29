"""
Defines interfaces that implementing classes must fulfill.
"""
from abc import ABCMeta, abstractmethod

class StorageConstruct(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def put(self, data, mime, family=None,
     extension=None, compression=None, compress_on_server=False,
     deletion_policy=None, compression_policy=None,
     meta=None,
     uid=None, keys=None
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
    def get(self, uid, read_key):
        raise NotImplementedError("get() must be overridden in child classes")
        
    @abstractmethod
    def describe(self, uid, read_key):
        raise NotImplementedError("describe() must be overridden in child classes")
        
class ControlConstruct(StorageConstruct, RetrievalConstruct):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def delete(self, uid, write_key):
        raise NotImplementedError("delete() must be overridden in child classes")
        
    @abstractmethod
    def query(self):
        raise NotImplementedError("query() must be overridden in child classes")
        
    @abstractmethod
    def update(self, uid, write_key, new={}, removed=(), deletion_policy=None, compression_policy=None):
        raise NotImplementedError("update_meta() must be overridden in child classes")
        

"""
Defines interfaces that implementing classes must fulfill.
"""
import abc

class StorageConstruct(object):
    __metaclass__ = abc.ABCMeta
    
    #Basis of the proxy implementation
    
    @abstractmethod
    def put(self, data, mime, ???):
        """
        Full implementations are possible. @abstractmethod just means that the method must be
        present in any derived classes, whether inherited or otherwise.
        """
        raise NotImplementedError("put() must be overridden in child classes")
        
        
class RetrievalConstruct(object):
    __metaclass__ = abc.ABCMeta
    
    #Basis of the caching proxy implementation
    #describe will be implemented as a pass-through on the proxy
    
    @abstractmethod
    def get(self, uid, read_key):
        raise NotImplementedError("get() must be overridden in child classes")
        
    @abstractmethod
    def describe(self, uid, read_key):
        raise NotImplementedError("describe() must be overridden in child classes")
        
class ControlConstruct(StorageConstruct, RetrievalConstruct):
    __metaclass__ = abc.ABCMeta
    
    #Basis of the main implementation
    
    @abstractmethod
    def delete(self, uid, write_key):
        raise NotImplementedError("delete() must be overridden in child classes")
        
    @abstractmethod
    def query(self, ???):
        raise NotImplementedError("query() must be overridden in child classes")
        
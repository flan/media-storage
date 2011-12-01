from abc import ABCMeta, abstractmethod
import logging

_logger = logging.getLogger("media_storage.backends.common")

class BaseBackend(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get(self, path):
        raise NotImplementedError("'get()' needs to be overridden in a subclass")
        
    @abstractmethod
    def put(self, path, data):
        raise NotImplementedError("'put()' needs to be overridden in a subclass")
        
    @abstractmethod
    def unlink(self, path, rmcontainer=False):
        raise NotImplementedError("'_unlink()' needs to be overridden in a subclass")
        
    @abstractmethod
    def file_exists(self, path):
        raise NotImplementedError("'file_exists()' needs to be overridden in a subclass")
        
    @abstractmethod
    def walk(self):
        raise NotImplementedError("'walk()' needs to be overridden in a subclass")
        
        
class Error(Exception):
    """
    The base exception common to this package.
    """
    
class FileNotFoundError(Error):
    """
    The identified file was not found.
    """
    
class PermissionsError(Error):
    """
    Insufficient permissions to perform the requested action.
    """
    
class CollisionError(Error):
    """
    A resource already exists with the target name.
    """
    
class NotEmptyError(Error):
    """
    Unable to unlink container because it is not empty.
    """
    
class NoSpaceError(Error):
    """
    No space remains on device.
    """
    
class NoFilehandleError(Error):
    """
    No filehandle could be allocated.
    """
    

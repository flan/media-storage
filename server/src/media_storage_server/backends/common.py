from abc import ABCMeta, abstractmethod
import logging

_logger = logging.getLogger("media_storage.backends.common")

class BaseBackend(object):
    __metaclass__ = ABCMeta
    _last_accessed_directory = None #A TLB-like placeholder
    
    @abstractmethod
    def get(self, path):
        _logger.debug("Retrieving filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._get(path)
        
    def _get(self, path):
        raise NotImplementedError("'_get()' needs to be overridden in a subclass")
        
    @abstractmethod
    def put(self, path, data):
        _logger.info("Setting filesystem entity at %(path)s..." % {
         'path': path,
        })
        directory = path[:path.rfind('/') + 1]
        if not directory == self._last_accessed_directory:
            try:
                self.mkdir(directory)
            except CollisionError: #Competition for directory ID
                pass
            self._last_accessed_directory = directory
        self._put(path, data)
        
    def _put(self, path, data):
        raise NotImplementedError("'_put()' needs to be overridden in a subclass")
        
    @abstractmethod
    def unlink(self, path, rmdir=False):
        """
        If `rmdir` is set, empty directories will be removed recursively.
        """
        _logger.info("Unlinking filesystem entity at %(path)s..." % {
         'path': path,
        })
        self._unlink(path)
        if rmdir:
            while True:
                path = path[:path.rfind('/') + 1]
                if not path: #Arrived at root
                    break
                    
                if not self.lsdir(path): #Directory empty; remove
                    _logger.info("Unlinking empty directory at %(path)s..." % {
                     'path': path,
                    })
                    try:
                        self.rmdir(path)
                    except NotEmptyError as e:
                        _logger.info("Directory at %(path)s unexpectedly found to be non-empty" % {
                         'path': path,
                        })
                        break
                else: #Directory not empty; bail
                    break
                    
    def _unlink(self, path):
        raise NotImplementedError("'_unlink()' needs to be overridden in a subclass")
        
    @abstractmethod
    def lsdir(self, path):
        _logger.debug("Retrieving list of filesystem contents at %(path)s..." % {
         'path': path,
        })
        return self._lsdir()
        
    def _lsdir(self, path):
        raise NotImplementedError("'_lsdir()' needs to be overridden in a subclass")
        
    @abstractmethod
    def mkdir(self, path):
        _logger.info("Creating directory at %(path)s..." % {
         'path': path,
        })
        self._mkdir(path)
        
    def _mkdir(self, path):
        raise NotImplementedError("'_mkdir()' needs to be overridden in a subclass")
        
    @abstractmethod
    def rmdir(self, path):
        _logger.debug("Unlinking directory at %(path)s..." % {
         'path': path,
        })
        self._rmdir(path)
        
    def _rmdir(self, path):
        raise NotImplementedError("'_rmdir()' needs to be overridden in a subclass")
        
    @abstractmethod
    def file_exists(self, path):
        _logger.debug("Testing existence of filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._file_exists(path)
        
    def _file_exists(self, path):
        raise NotImplementedError("'_file_exists()' needs to be overridden in a subclass")
        
    @abstractmethod
    def is_dir(self, path):
        _logger.debug("Testing directory status of filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._is_dir()
        
    def _is_dir(self, path):
        raise NotImplementedError("'is_dir()' needs to be overridden in a subclass")
        
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
    Unable to unlink directory because it is not empty.
    """
    
class NoSpaceError(Error):
    """
    No space remains on device.
    """
    
class NoFilehandleError(Error):
    """
    No filehandle could be allocated.
    """
    

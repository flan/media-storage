from abc import ABCMeta, abstractmethod
import logging

import common
from common import (
 Error,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)

_logger = logging.getLogger("media_storage.backends.directory")

class DirectoryBackend(common.BaseBackend):
    """
    A backend base-class for directory-based filesystems.
    """
    __metaclass__ = ABCMeta
    _last_accessed_directory = None #A TLB-like placeholder
    
    def get(self, path):
        _logger.debug("Retrieving filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._get(path)
        
    @abstractmethod
    def _get(self, path):
        raise NotImplementedError("'_get()' needs to be overridden in a subclass")
        
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
        
    @abstractmethod
    def _put(self, path, data):
        raise NotImplementedError("'_put()' needs to be overridden in a subclass")
        
    def unlink(self, path, rmcontainer=False):
        """
        If `rmcontainer` is set, empty directories will be removed recursively.
        """
        _logger.info("Unlinking filesystem entity at %(path)s..." % {
         'path': path,
        })
        self._unlink(path)
        if rmcontainer:
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
                    
    @abstractmethod
    def _unlink(self, path):
        raise NotImplementedError("'_unlink()' needs to be overridden in a subclass")
        
    def mkdir(self, path):
        _logger.info("Creating directory at %(path)s..." % {
         'path': path,
        })
        self._mkdir(path)
        
    @abstractmethod
    def _mkdir(self, path):
        raise NotImplementedError("'_mkdir()' needs to be overridden in a subclass")
        
    def rmdir(self, path):
        _logger.debug("Unlinking directory at %(path)s..." % {
         'path': path,
        })
        self._rmdir(path)
        
    @abstractmethod
    def _rmdir(self, path):
        raise NotImplementedError("'_rmdir()' needs to be overridden in a subclass")
        
    def file_exists(self, path):
        _logger.debug("Testing existence of filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._file_exists(path)
        
    @abstractmethod
    def _file_exists(self, path):
        raise NotImplementedError("'_file_exists()' needs to be overridden in a subclass")
        
    def walk(self):
        _logger.debug("Walking filesystem...")
        return self._walk(path)
        
    @abstractmethod
    def _walk(self):
        raise NotImplementedError("'walk()' needs to be overridden in a subclass")
        

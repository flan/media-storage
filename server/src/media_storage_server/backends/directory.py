"""
media-storage_server.backends.directory
=======================================

Provides an abstraction and partial implementation of directory-oriented backends.

Legal
+++++
 This file is part of media-storage.
 media-storage is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 
 (C) Neil Tallim, 2012 <flan@uguu.ca>
"""
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
    _last_accessed_directory = None #A TLB-like placeholder, preventing unnecessary directory-creation requests
    
    def get(self, path):
        """
        See ``common.BaseBackend.get()``.
        """
        _logger.debug("Retrieving filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._get(path)
        
    @abstractmethod
    def _get(self, path):
        raise NotImplementedError("'_get()' needs to be overridden in a subclass")
        
    def put(self, path, data, tempfile):
        """
        See ``common.BaseBackend.put()``.
        
        If the required directory structure does not yet exist, it is created before the data is
        written.
        """
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
        self._put(path, data, tempfile)
        
    @abstractmethod
    def _put(self, path, data, tempfile):
        raise NotImplementedError("'_put()' needs to be overridden in a subclass")
        
    def make_permanent(self, path):
        """
        See ``common.BaseBackend.make_permanent()``.
        """
        self._make_permanent(path)
        
    @abstractmethod
    def _make_permanent(self, path):
        raise NotImplementedError("'_make_permanent()' needs to be overridden in a subclass")
        
    def unlink(self, path, rmcontainer=False):
        """
        See ``common.BaseBackend.unlink()``.
        
        If `rmcontainer` is set, directories are recursively unlinked until the root level is
        reached, so long as they are empty.
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
                    
                if not self._lsdir(path): #Directory empty; remove
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
        """
        Creates a directory-chain on the filesystem, until `path` is reached.
        """
        _logger.info("Creating directory at %(path)s..." % {
         'path': path,
        })
        self._mkdir(path)
        
    @abstractmethod
    def _mkdir(self, path):
        raise NotImplementedError("'_mkdir()' needs to be overridden in a subclass")
        
    def rmdir(self, path):
        """
        Removes the directory identified as `path` from the filesystem.
        """
        _logger.debug("Unlinking directory at %(path)s..." % {
         'path': path,
        })
        self._rmdir(path)
        
    @abstractmethod
    def _rmdir(self, path):
        raise NotImplementedError("'_rmdir()' needs to be overridden in a subclass")
        
    def file_exists(self, path):
        """
        See ``common.BaseBackend.file_exists()``.
        """
        _logger.debug("Testing existence of filesystem entity at %(path)s..." % {
         'path': path,
        })
        return self._file_exists(path)
        
    @abstractmethod
    def _file_exists(self, path):
        raise NotImplementedError("'_file_exists()' needs to be overridden in a subclass")
        
    def walk(self):
        """
        See ``common.BaseBackend.walk()``.
        """
        _logger.debug("Walking filesystem...")
        return self._walk(path)
        
    @abstractmethod
    def _walk(self):
        raise NotImplementedError("'walk()' needs to be overridden in a subclass")
        

"""
media-storage_server.backends.common
====================================

Provides high-level abstract descriptions of how to interact with a storage target, including
exceptions.
 
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

_logger = logging.getLogger("media_storage.backends.common")

class BaseBackend(object):
    """
    An abstract interface for what a filesystem backend instance needs to implement.
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def resolve_path(record):
        """
        Provides the path to a file, given its record.
        """
        raise NotImplementedError("'resolve_path()' needs to be overridden in a subclass")
        
    @abstractmethod
    def get(self, path):
        """
        Retrieves the requested file from the backend as a file-like object, given a
        backend-specific `path`.
        """
        raise NotImplementedError("'get()' needs to be overridden in a subclass")
        
    @abstractmethod
    def put(self, path, data, tempfile):
        """
        Stores the given `data`, a file-like object, in the backend, given a backend-specific
        `path`.
        
        If `tempfile` is True, the file is written in a manner such that it will not be committed
        until `make_permanent()` is called.
        """
        raise NotImplementedError("'put()' needs to be overridden in a subclass")
        
    @abstractmethod
    def make_permanent(self, path):
        """
        Makes a file stored at `path` via `put(tempfile=True)` permanent.
        """
        raise NotImplementedError("'make_permanent()' needs to be overridden in a subclass")
        
    @abstractmethod
    def unlink(self, path, rmcontainer=False):
        """
        Removes the indicated file from the backend, given a backend-specific `path`.
        `rmcontainer`, if True, causes the container-structure of the file to be pruned as much as
        possible, provided that it is empty.
        """
        raise NotImplementedError("'_unlink()' needs to be overridden in a subclass")
        
    @abstractmethod
    def file_exists(self, path):
        """
        Indicates whether a file exists at a backend-specific `path`.
        """
        raise NotImplementedError("'file_exists()' needs to be overridden in a subclass")
        
    @abstractmethod
    def walk(self):
        """
        Provides a generator that enumerates every file in the filesystem, yielding results as
        (sub-path:str, [filename:str]) tuples, where the sub-path is relative to the end of the
        filesystem's location as specified in the instantiating URI. Concatenating the sub-path and
        filename will allow use by other methods.
        """
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
    

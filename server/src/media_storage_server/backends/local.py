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
import logging
import os

from common import (
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
import directory

_CHUNK_SIZE = 32 * 1024 #Work with 32K chunks
_TEMPFILE_EXTENSION = '.temp'

_logger = logging.getLogger("media_storage.backends.local")

def _handle_error(e):
    """
    A generic error-handling construct that raises the appropriate exception,
    depending on the problem that occurred.
    """
    if e.errno == 2:
        raise FileNotFoundError(str(e))
    elif e.errno == 13:
        raise PermissionsError(str(e))
    elif e.errno == 17:
        raise CollisionError(str(e))
    elif e.errno == 24:
        raise NoFilehandleError(str(e))
    elif e.errno == 28:
        raise NoSpaceError(str(e))
        
class LocalBackend(directory.DirectoryBackend):
    """
    Defines a final implementation for local contemporary filesystems.
    """
    _path = None #The path on which this backend operates
    
    def __init__(self, path):
        """
        Ensures that `path` ends with a directory delimiter.
        """
        if not path.endswith(('/', '\\')):
            self._path = path + os.path.sep
        else:
            self._path = path
            
    def _get(self, path):
        """
        Returns an open file handle for the requested file, or raises an exception.
        """
        target_path = self._path + path
        try:
            return open(target_path, 'rb')
        except IOError as e:
            _logger.error("Unable to open file at %(path)s: %(error)s" % {
             'path': target_path,
             'error': str(e),
            })
            _handle_error(e)
            raise
            
    def _put(self, path, data, tempfile):
        """
        Attempts to write all content from `data` to the location indicated by `path`, raising an
        exception on error.
        
        `data` is not seeked back to the beginning after this operation completes.
        
        `tempfile` indicates whether a special extension should be applied.
        """
        target_path = self._path + path
        if tempfile:
            target_path += _TEMPFILE_EXTENSION
            
        try:
            target = open(target_path, 'wb')
        except IOError as e:
            _logger.error("Unable to open file for writing at %(path)s: %(error)s" % {
             'path': target_path,
             'error': str(e),
            })
            _handle_error(e)
            raise
        else:
            try:
                global _CHUNK_SIZE
                while True:
                    chunk = data.read(_CHUNK_SIZE)
                    if chunk:
                        target.write(chunk)
                    else:
                        break
            except Exception:
                try:
                    target.close()
                except Exception:
                    _logger.error("Unable to close handle for abandoned file at %(path)s: %(error)s" % {
                     'path': target_path,
                     'error': str(e),
                    })
                _logger.error("Unable to write content to file at %(path)s: %(error)s" % {
                 'path': target_path,
                 'error': str(e),
                })
                try:
                    self._unlink(target_path)
                except Exception as e:
                    _logger.error("Unable to unlink incomplete file at %(path)s: %(error)s" % {
                     'path': target_path,
                     'error': str(e),
                    })
                raise
            else:
                try:
                    target.close()
                except Exception as e:
                    _logger.error("Unable to close handle for file at %(path)s: %(error)s" % {
                     'path': target_path,
                     'error': str(e),
                    })
                    
    def _make_permanent(self, path):
        """
        Makes the tempfile at `path` permanent by removing its extension.
        """
        target_path = self._path + path
        tempfile_path = target_path + _TEMPFILE_EXTENSION
        
        try:
            os.rename(tempfile_path, target_path)
        except IOError as e:
            _logger.error("Unable to make file permanent at %(path)s: %(error)s" % {
             'path': target_path,
             'error': str(e),
            })
            _handle_error(e)
            raise
            
    def _action(self, path, handler):
        """
        Performs a generic action, `handler`, which takes `path` as an argument. On error, an
        exception is raised; on success, the result of invoking `handler` is returned.
        """
        target_path = self._path + path
        try:
            return handler(target_path)
        except (IOError, OSError) as e:
            _logger.error("Unable to perform requested operation on %(path)s: %(error)s" % {
             'path': target_path,
             'error': str(e),
            })
            _handle_error(e)
            raise
            
    def _unlink(self, path):
        """
        Removes the file at `path`, raising an exception on failure.
        """
        self._action(path, os.unlink)
        
    def _lsdir(self, path):
        """
        Lists all files in the directory.
        """
        target_path = self._path + path
        try:
            return os.listdir(target_path)
        except (IOError, OSError) as e:
            _logger.error("Unable to list directory at %(path)s: %(error)s" % {
             'path': target_path,
             'error': str(e),
            })
            _handle_error(e)
            raise
            
    def _mkdir(self, path):
        """
        Creates the requested `path`, and all intermediate paths, raising an exception on failure.
        """
        target_path = self._path + path
        try:
            os.makedirs(target_path, 0750)
        except (IOError, OSError) as e:
            _logger.error("Unable to create directory at %(path)s: %(error)s" % {
             'path': target_path,
             'error': str(e),
            })
            _handle_error(e)
            raise
            
    def _rmdir(self, path):
        """
        Removes the requested `path`, which must be a terminal node and be empty.
        """
        self._action(path, os.rmdir)
        
    def _file_exists(self, path):
        """
        Indicates, with a boolean value, whether a file exists at `path`. If the file cannot be
        read for any reason, False is returned.
        """
        return os.path.exists(self._path + path)
        
    def _walk(self):
        """
        Provides a generator that enumerates every file in the system, as tuples of (path:str,
        [file:str]).
        """
        for (root, dirnames, files) in os.walk(self.path):
            yield (root[len(self._path):], files)
            

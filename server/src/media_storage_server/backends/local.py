import logging
import os

from common import (
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
import directory

_CHUNK_SIZE = 32 * 1024 #Work with 32K chunks

_logger = logging.getLogger("media_storage.backends.local")

def _handle_error(e):
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
    _path = None #The path on which this backend operates
    
    def __init__(self, path):
        if not path.endswith(('/', '\\')):
            self._path = path + os.path.sep
        else:
            self._path = path
            
    def _get(self, path):
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
            
    def _put(self, path, data):
        target_path = self._path + path
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
                    
    def _action(self, path, handler):
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
        self._action(path, os.unlink)
        
    def _mkdir(self, path):
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
        self._action(path, os.rmdir)
        
    def _file_exists(self, path):
        return os.path.exists(self._path + path)
        
    def _walk(self):
        for (root, dirnames, files) in os.walk(self.path):
            yield (root[len(self._path):], files)
            

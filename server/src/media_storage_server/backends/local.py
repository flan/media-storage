import os

from common import (
 BaseBackend,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError,
)

_CHUNK_SIZE = 32 * 1024 #Work with 32K chunks

def _handle_error(e):
    if e.errno == 2:
        raise FileNotFoundError('Unable to open %(path)s' % {
         'path': path,
        })
    elif e.errno == 13:
        raise PermissionsError('Unable to access %(path)s' % {
         'path': path,
        })
    elif e.errno == 17:
        raise CollisionError('Unable to create %(path)s' % {
         'path': path,
        })
        
class LocalBackend(BaseBackend):
    _path = None #The path on which this backend operates
    
    def __init__(self, path):
        if not path.endswith('/', '\\'):
            self._path = path + os.path.sep
        else:
            self._path = path
            
    def _get(self, path):
        try:
            return open(path, 'rb')
        except IOError as e:
            _handle_error(e)
            raise
            
    def _put(self, path, data):
        try:
            target = open(path, 'wb')
        except IOError as e:
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
                    pass
                try:
                    self._unlink(path)
                except Exception as e:
                    #Log e
                    pass
                raise
            else:
                try:
                    target.close()
                except Exception as e:
                    #Log e
                    pass
                    
    def _action, self, path, handler):
        try:
            return handler(path)
        except (IOError, OSError) as e:
            _handle_error(e)
            raise
            
    def _unlink(self, path):
        self._action(path, os.unlink)
        
    def _lsdir(self, path):
        self._action(path, os.listdir)
        
    def _mkdir(self, path):
        self._action(path, os.mkdir)
        
    def _rmdir(self, path):
        self._action(path, os.rmdir)
        
    def _file_exists(self, path):
        return os.path.exists(path)
        
    def _is_dir(self, path):
        return os.path.isdir(path)
        

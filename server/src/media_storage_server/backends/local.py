import os

from common import (
 BaseBackend,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError,
)

_CHUNK_SIZE = 32 * 1024 #Work with 32K chunks

def _handle_error(e):
    if e.errno == 2:
        raise FileNotFoundError(str(e))
    elif e.errno == 13:
        raise PermissionsError(str(e))
    elif e.errno == 17:
        raise CollisionError(str(e))
        
class LocalBackend(BaseBackend):
    _path = None #The path on which this backend operates
    
    def __init__(self, path):
        if not path.endswith(('/', '\\')):
            self._path = path + os.path.sep
        else:
            self._path = path
            
    def _get(self, path):
        try:
            return open(self._path + path, 'rb')
        except IOError as e:
            _handle_error(e)
            raise
            
    def _put(self, path, data):
        try:
            target = open(self._path + path, 'wb')
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
                    self._unlink(self._path + path)
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
                    
    def _action(self, path, handler):
        try:
            return handler(self._path + path)
        except (IOError, OSError) as e:
            _handle_error(e)
            raise
            
    def _unlink(self, path):
        self._action(path, os.unlink)
        
    def _lsdir(self, path):
        self._action(path, os.listdir)
        
    def _mkdir(self, path):
        try:
            os.makedirs(self._path + path, 0750)
            """path_fragments = [f for f in path.split('/') if f]
            for i in range(len(path_fragments)):
                subpath = self._path + '/'.join(path_fragments[:i + 1])
                print subpath
                if not self._is_dir(subpath):
                    os.mkdir(subpath, 0750)"""
        except (IOError, OSError) as e:
            _handle_error(e)
            raise
            
    def _rmdir(self, path):
        self._action(path, os.rmdir)
        
    def _file_exists(self, path):
        return os.path.exists(self._path + path)
        
    def _file_size(self, path):
        return self._action(path, os.stat).st_size
        
    def _is_dir(self, path):
        return os.path.isdir(self._path + path)
        

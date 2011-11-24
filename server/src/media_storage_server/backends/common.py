class BaseBackend(object):
    _base_path = None #The path relative to the filesystem root at which data-storage begins
    _last_accessed_directory = None #A TLB-like placeholder
    
    def get(self, path):
        return self._get(path)
        
    def _get(self, path):
        raise NotImplementedError("'_get()' needs to be overridden in a subclass")
        
    def put(self, path, data):
        directory = path[:path.rfind('/') + 1]
        if not directory == self._last_accessed_directory:
            self.mkdir(directory)
            self._last_accessed_path = directory
        self._put(path, data)
        
    def _put(self, path, data):
        raise NotImplementedError("'_put()' needs to be overridden in a subclass")
        
    def unlink(self, path, rmdir=False):
        """
        If `rmdir` is set, empty directories will be removed recursively.
        """
        self._unlink(path)
        if rmdir:
            while True:
                path = path[:path.rfind('/') + 1]
                if not path: #Arrived at root
                    break
                    
                if not self.lsdir(path): #Directory empty; remove
                    try:
                        self.rmdir(path)
                    except NotEmptyError as e:
                        #Log e
                        break
                else: #Directory not empty; bail
                    break
                    
    def _unlink(self, path):
        raise NotImplementedError("'_unlink()' needs to be overridden in a subclass")
        
    def lsdir(self, path):
        return self._lsdir()
        
    def _lsdir(self, path):
        raise NotImplementedError("'_lsdir()' needs to be overridden in a subclass")
        
    def mkdir(self, path):
        self._mkdir(path)
        
    def _mkdir(self, path):
        raise NotImplementedError("'_mkdir()' needs to be overridden in a subclass")
        
    def rmdir(self, path):
        self._rmdir(path)
        
    def _rmdir(self, path):
        raise NotImplementedError("'_rmdir()' needs to be overridden in a subclass")
        
    def file_exists(self, path):
        return self._file_exists(path)
        
    def _file_exists(self, path):
        raise NotImplementedError("'_file_exists()' needs to be overridden in a subclass")
        
    def is_dir(self, path):
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
    

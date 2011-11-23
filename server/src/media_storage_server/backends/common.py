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
                    self.rmdir(path)
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
        
    def mkdir(self, path):
        raise NotImplementedError("'_mkdir()' needs to be overridden in a subclass")
        
    def rmdir(self, path):
        self._rmdir(path)
        
    def _rmdir(self, path):
        raise NotImplementedError("'_rmdir()' needs to be overridden in a subclass")
        
class Error(Exception):
    """
    The base exception common to this package.
    """
    
class FileNotFoundError(Error):
    """
    The identified file was not found.
    """
    

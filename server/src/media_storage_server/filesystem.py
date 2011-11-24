"""
Provides a means of resolving and accessing filesystem targets, regardless of
backend.
"""
import time

import backends
from backends import (
 Error,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError,
)
from config import CONFIG

class Filesystem(object):
    _backend = None #The backend used to manage files
    
    def __init__(self, uri):
        self._backend = backends.get_backend(uri)
        
    def get(self, record):
        return self._backend.get(self._resolve_path(record))
        
    def put(self, record, data):
        self._backend.put(self._resolve_path(record), data)
        
    def unlink(self, record):
        """
        Removes the file associated with the given `record`.
        
        If the directory in which the file resides is old enough that new files cannot resonably
        be placed inside (2 * resolution in minutes), then directories may be removed to free
        allocation resources.
        """
        self._backend.unlink(
         self._resolve_path(record),
         rmdir=(time.time() - record['physical']['ctime'] > CONFIG.filesystem_directory_resolution * 120)
        )
        
    def file_exists(self, record):
        return self._backend.file_exists(self._resolve_path(record))
        
    def file_size(self, record):
        return self._backend.file_size(self._resolve_path(record))
        
    def lsdir(self, path):
        return self._backend.lsdir(path)
        
    def is_dir(self, path):
        return self._backend.is_dir(path)
        
    def _assemble_filename(self, record):
        filename_parts = (record['_id'], record['physical']['format']['ext'], record['physical']['format']['comp'])
        return '.'.join((part for part in filename_parts if part))
        
    def _resolve_path(self, record):
        ts = time.gmtime(record['physical']['ctime'])
        return '%(year)i/%(month)i/%(day)i/%(hour)i/%(min)i/' % {
         'year': ts.tm_year,
         'month': ts.tm_mon,
         'day': ts.tm_mday,
         'hour': ts.tm_hour,
         'min': ts.tm_min - ts.tm_min % CONFIG.filesystem_directory_resolution,
        } + self._assemble_filename(record)
        

"""
Provides a means of resolving and accessing filesystem targets, regardless of
backend.
"""
import time

import backends
from config import CONFIG

class Filesystem(object):
    _backend = None #The backend used to manage files
    
    def __init__(self, uri):
        self._backend = backends.get_backend(uri)
        
    def get(self, record):
        return backend.get(self._resolve_path(record))
        
    def put(self, record, data):
        backend.put(self._resolve_path(record), data)
        
    def unlink(self, record):
        """
        Removes the file associated with the given `record`.
        
        If the directory in which the file resides is old enough that new files cannot resonably
        be placed inside (2 * resolution in minutes), then directories may be removed to free
        allocation resources.
        """
        backend.unlink(
         self._resolve_path(record),
         rmdir=(time.time() - record['physical']['ctime'] > CONFIG.filesystem_directory_resolution * 120)
        )
        
    def _resolve_path(self, record):
        ts = time.gmtime(record['physical']['ctime'])
        directory = '%(year)i/%(month)i/%(day)i/%(hour)i/%(min)i/' % {
         'year': ts.tm_year,
         'month': ts.tm_mon,
         'day': ts.tm_mday,
         'hour': ts.tm_hour,
         'min': ts.tm_min - ts.tm_min % CONFIG.filesystem_directory_resolution,
        }
        
        filename_parts = (record['_id'], record['format'].get('ext'), record['format'].get('comp'))
        
        return '%(directory)s%(filename)s' % {
         'directory': directory,
         'filename': '.'.join((part for part in filename_parts if part))
        }
        

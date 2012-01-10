"""
Provides a means of resolving and accessing filesystem targets, regardless of
backend.
"""
import logging
import time

import backends
from backends import (
 Error,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
from config import CONFIG

_logger = logging.getLogger('media_storage.filesystem')
    
def resolve_path(record):
    ts = time.gmtime(record['physical']['ctime'])
    return '%(year)i/%(month)i/%(day)i/%(hour)i/%(min)i/%(uid)s' % {
     'year': ts.tm_year,
     'month': ts.tm_mon,
     'day': ts.tm_mday,
     'hour': ts.tm_hour,
     'min': ts.tm_min - ts.tm_min % record['physical']['minRes'],
     'uid': record['_id'],
    }
    

class Filesystem(object):
    _backend = None #The backend used to manage files
    
    def __init__(self, uri):
        self._backend = backends.get_backend(uri)
        
    def get(self, record):
        _logger.debug("Retrieving filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        return self._backend.get(resolve_path(record))
        
    def put(self, record, data, tempfile=False):
        _logger.info("Setting filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        self._backend.put(resolve_path(record), data, tempfile)
        
    def make_permanent(record):
        _logger.debug("Making filesystem entity for %(uid)s permanent..." % {
         'uid': record['_id'],
        })
        self._backend.make_permanent(resolve_path(record))
        
    def unlink(self, record):
        """
        Removes the file associated with the given `record`.
        
        If the directory in which the file resides is old enough that new files cannot resonably
        be placed inside (2 * resolution in minutes), then directories may be removed to free
        allocation resources.
        """
        _logger.info("Unlinking filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        self._backend.unlink(
         resolve_path(record),
         rmcontainer=(time.time() - record['physical']['ctime'] > CONFIG.storage_minute_resolution * 120)
        )
        
    def file_exists(self, record):
        _logger.debug("Testing existence of filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        return self._backend.file_exists(resolve_path(record))
        
    def walk(self):
        """
        Returns a generator that recursively traverses the whole filesystem.
        """
        return self._backend.walk()
        

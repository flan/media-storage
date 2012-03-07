"""
media-storage.database
======================

Provides a means of resolving and accessing filesystem targets, regardless of
backend.

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
import time

import backends
from backends import (
 Error,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
from config import CONFIG

_logger = logging.getLogger('media_storage.filesystem')

class Filesystem(object):
    """
    An abstract notion of a filesystem, which may wrap conventional directory systems,
    BLOB-in-database systems, or most things that don't exist yet, as long as they support unique
    identifiers of some sort.
    """
    _backend = None #The backend used to manage files
    
    def __init__(self, uri):
        self._backend = backends.get_backend(uri)
        
    def resolve_path(self, record):
        """
        Determines the filesystem path of the file associated with `record`.
        """
        return self._backend.resolve_path(record)
        
    def get(self, record):
        """
        Retrieves the data associated with `record`.
        """
        _logger.debug("Retrieving filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        return self._backend.get(self.resolve_path(record))
        
    def put(self, record, data, tempfile=False):
        """
        Stores `data` in a location identifiable through `record`. If `tempfile` is set, the file is
        written with temporary markings.
        """
        _logger.info("Setting filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        self._backend.put(self.resolve_path(record), data, tempfile)
        
    def make_permanent(self, record):
        """
        Removes the "temporary" status of the file associated with `record`.
        """
        _logger.debug("Making filesystem entity for %(uid)s permanent..." % {
         'uid': record['_id'],
        })
        self._backend.make_permanent(self.resolve_path(record))
        
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
         self.resolve_path(record),
         rmcontainer=(time.time() - record['physical']['ctime'] > CONFIG.storage_minute_resolution * 120)
        )
        
    def file_exists(self, record):
        """
        Provides a boolean value that indicates whether the file associated with `record` exists.
        """
        _logger.debug("Testing existence of filesystem entity for %(uid)s..." % {
         'uid': record['_id'],
        })
        return self._backend.file_exists(self.resolve_path(record))
        
    def walk(self):
        """
        Returns a generator that recursively traverses the whole filesystem.
        """
        return self._backend.walk()
        

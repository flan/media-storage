"""
media-storage_server.maintenance
================================

Defines threads that handle system cleanup tasks, like compression and deletion policies, purging
entries from the database if the corresponding file is manualy deleted, and deleting files if
database entries are deleted.

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
import re
import threading
import time

from config import CONFIG
import compression
import database
import filesystem
import state

#Window structures to determine when threads may run
DELETION_WINDOWS = None
COMPRESSION_WINDOWS = None
DATABASE_WINDOWS = None
FILESYSTEM_WINDOWS = None

_logger = logging.getLogger("media_storage.maintainence")

def parse_windows():
    """
    Interprets the execution windows defined in the configuration file to determine when the threads
    can actually operate.
    """
    global DELETION_WINDOWS
    DELETION_WINDOWS = _parse_windows(CONFIG.maintainer_deletion_windows, 'deletion policy')
    global COMPRESSION_WINDOWS
    COMPRESSION_WINDOWS = _parse_windows(CONFIG.maintainer_compression_windows, 'compression policy')
    global DATABASE_WINDOWS
    DATABASE_WINDOWS = _parse_windows(CONFIG.maintainer_database_windows, 'database integrity')
    global FILESYSTEM_WINDOWS
    FILESYSTEM_WINDOWS = _parse_windows(CONFIG.maintainer_filesystem_windows, 'filesystem integrity')
    
def _parse_windows(definition, name):
    """
    Provides the actual interpretation logic for thread-execution-windows.
    """
    _DAY_MAP = {
     'mo': 0,
     'tu': 1,
     'we': 2,
     'th': 3,
     'fr': 4,
     'sa': 5,
     'su': 6,
    }
    _WINDOW_DAY_RE = re.compile(r'(?P<day>(?:' + '|'.join(_DAY_MAP) +  r'))\[(?P<times>\d{1,2}:\d{2}\.\.\d{1,2}:\d{2}(?:,\d{1,2}:\d{2}\.\.\d{1,2}:\d{2})*?)\]')
    
    windows = {}
    for day in definition.lower().split():
        match = _WINDOW_DAY_RE.match(day)
        if match:
            _logger.info("Validated execution windows for %(name)s maintainer: %(windows)s" % {
             'name': name,
             'windows': day,
            })
            times = []
            for timerange in match.group('times').split(','):
                (start, end) = timerange.split('..', 1)
                start = tuple((int(v) for v in start.split(':', 1)))
                end = tuple((int(v) for v in end.split(':', 1)))
                times.append((
                 start[0] * 60 + start[1],
                 end[0] * 60 + end[1],
                ))
            windows[_DAY_MAP[match.group('day')]] = tuple(times)
    return windows
    
class _Maintainer(threading.Thread):
    """
    Provides the foundation of all maintenance threads.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        
    def _within_window(self, windows):
        """
        Provides a boolean value indicating whether the thread can execute or not.
        """
        ts = time.localtime()
        tc = ts.tm_hour * 60 + ts.tm_min
        ranges = windows.get(ts.tm_wday)
        if not ranges:
            return False
            
        for (start, end) in ranges:
            if start <= tc < end:
                return True
        return False
        
class _PolicyMaintainer(_Maintainer):
    """
    Provides an abstract definition of the policy-managing maintener threads.
    """
    def __init__(self):
        _Maintainer.__init__(self)
        
    def run(self):
        """
        Queries the database, looking for any records that match policy criteria. If any matches are
        found, they're processed, and the operation continues until no new records are discovered.
        """
        while True:
            while not self._within_window(self._windows):
                _logger.debug("Not in execution window; sleeping")
                time.sleep(60)
                
            while True:
                records_processed = False
                for record in database.enumerate_where({
                 '$or': [
                  {self._fixed_field: {'$lt': int(time.time())}},
                  {self._stale_query: {'$lt': int(time.time())}},
                 ],
                }):
                    _logger.info("Discovered candidate record: %(uid)s" % {
                     'uid': record['_id'],
                    })
                    #Some records may fail to be processed for a variety of reasons; they shouldn't be considered active
                    records_processed = self._process_record(record) or records_processed
                if not records_processed: #Nothing left to do
                    break
                    
            _logger.debug("All records processed; sleeping")
            time.sleep(self._sleep_period)
            
    def _process_record(self, record):
        """
        Performs any policy-specific actions on the given `record`.
        """
        raise NotImplementedError("_process_record() must be overridden in a subclass")
        
class DeletionMaintainer(_PolicyMaintainer):
    """
    Removes records and files when their policy settings say they should be deleted.
    """
    def __init__(self):
        _PolicyMaintainer.__init__(self)
        self.name = 'deletion-maintainer'
        self._windows = DELETION_WINDOWS
        self._stale_query = 'policy.delete.staleTime'
        self._fixed_field = 'policy.delete.fixed'
        self._sleep_period = CONFIG.maintainer_deletion_sleep
        
    def _process_record(self, record):
        """
        Determines whether the given `record` is a candidate for deletion, removing it and the
        associated file if it is.
        """
        _logger.info("Unlinking record...")
        filesystem = state.get_filesystem(record['physical']['family'])
        try:
            filesystem.unlink(record)
        except Exception as e:
            _logger.warn("Unable to unlink record: %(error)s" % {
             'error': str(e),
            })
            return False
        else:
            database.drop_record(record['_id'])
            return True
            
class CompressionMaintainer(_PolicyMaintainer):
    """
    Compresses files when their policy settings say they should be compressed.
    """
    def __init__(self):
        _PolicyMaintainer.__init__(self)
        self.name = 'compression-maintainer'
        self._stale_query = 'policy.compress.staleTime'
        self._fixed_field = 'policy.compress.fixed'
        self._sleep_period = CONFIG.maintainer_compression_sleep
        self._windows = COMPRESSION_WINDOWS
        
    def _process_record(self, record):
        """
        Determines whether the given `record` is a candidate for compression, compressing the
        associated file and updating the record if it is.
        """
        _logger.info("Compressing record '%(uid)s'..." % {
         'uid': record['_id'],
        })
        current_compression = record['physical']['format'].get('comp')
        target_compression = record['policy']['compress'].get('comp')
        if current_compression == target_compression:
            _logger.debug("File already compressed in target format")
            record['policy']['compress'].clear() #Drop the compression policy
            try:
                database.update_record(record)
            except Exception as e:
                _logger.error("Unable to update record to reflect already-applied compression; compression routine will retry later: %(error)s" % {
                 'error': str(e),
                })
                return False
            else:
                return True
                
        filesystem = state.get_filesystem(record['physical']['family'])
        data = filesystem.get(record)
        if current_compression: #Must be decompressed first
            _logger.info("Decompressing file...")
            data = compression.get_decompressor(current_compression)(data)
        data = compression.get_compressor(target_compression)(data)
        
        _logger.info("Updating entity...")
        old_format = record['physical']['format'].copy()
        record['physical']['format']['comp'] = target_compression
        try:
            filesystem.put(record, data)
        except Exception as e: #Harmless backout point
            _logger.warn("Unable to write compressed file to disk; backing out with no consequences")
            return False
        else:
            record['policy']['compress'].clear() #Drop the compression policy
            try:
                database.update_record(record)
            except Exception as e: #Results in wasted space until the next attempt
                _logger.error("Unable to update record; old file will be served, and new file will be replaced on a subsequent compression attempt: %(error)s" % {
                 'error': str(e),
                })
                return False
            else:
                record['physical']['format'] = old_format
                try:
                    filesystem.unlink(record)
                except Exception as e: #Results in wasted space, but non-fatal
                    _logger.error("Unable to unlink old file; space non-recoverable unless unlinked manually: %(family)r | %(file)s : %(error)s" % {
                     'family': record['physical']['family'],
                     'file': filesystem.resolve_path(record),
                     'error': str(e),
                    })
                return True
                
class DatabaseMaintainer(_Maintainer):
    """
    Iterates over the database and removes records that are not associated with filesystem entries.
    """
    def __init__(self):
        _Maintainer.__init__(self)
        self.name = 'database-maintainer'
        
    def run(self):
        """
        Cycles through every database record in order, removing any records associated
        with files that do not exist.
        """
        ctime = -1.0
        while True:
            while not self._within_window(DATABASE_WINDOWS):
                _logger.debug("Not in execution window; sleeping" % {
                 'name': self.name,
                })
                time.sleep(60)
                
            records_retrieved = False
            for record in database.enumerate_all(ctime):
                ctime = record['physical']['ctime']
                records_retrieved = True
                
                filesystem = state.get_filesystem(record['physical']['family'])
                if not filesystem.file_exists(record):
                    _logger.warn("Discovered database record for '%(uid)s' without matching file; dropping record..." % {
                     'uid': record['_id'],
                    })
                    database.drop_record(record['_id'])
                    
            if not records_retrieved: #Cycle complete
                _logger.debug("All records processed; sleeping")
                time.sleep(CONFIG.maintainer_database_sleep)
                ctime = -1.0
                
class FilesystemMaintainer(_Maintainer):
    """
    Iterates over the filesystem and removes files that are not associated with database records.
    
    This thread should be disabled by default, since it would allow for the deletion of all data if
    the Mongo database is dropped for any reason, and, in smaller data-centres, a full filesystem
    backup may not exist.
    """
    def __init__(self):
        _Maintainer.__init__(self)
        self.name = 'filesystem-maintainer'
        
    def run(self):
        """
        Cycles through every filesystem entry in order, removing any files associated
        with database records that do not exist.
        """
        while True:
            for family in state.get_families():
                _logger.info("Processing family %(family)r..." % {
                 'family': family,
                })
                filesystem = state.get_filesystem(family)
                self._walk(filesystem.walk())
                
            _logger.debug("All records processed; sleeping")
            time.sleep(CONFIG.maintainer_filesystem_sleep)
            
    def _walk(self, walker):
        """
        Traverses the filesystem by iterating over `walker`, checking with the database to ensure
        that every encountered file has a corresponding record. If not, the file is unlinked.
        """
        try:
            for (path, files) in walker:
                for filename in files:
                    try:
                        if not self._keep_file(filename):
                            _logger.warn("Discovered orphaned file '%(name)s'; unlinking..." % {
                             'name': filename,
                            })
                            try:
                                filesystem.unlink(path + '/' + filename)
                            except Exception as e:
                                _logger.warn("Unable to unlink file: %(error)s" % {
                                 'error': str(e),
                                })
                    except Exception as e:
                        _logger.warn("Unable to query database: %(error)s" % {
                         'error': str(e),
                        })
        except Exception as e:
            _logger.warn("Unable to traverse filesystem: %(error)s" % {
             'error': str(e),
            })
            
    def _keep_file(self, filename):
        """
        Determines, through a database query, whether the given `filename` has a corresponding
        database record.
        """
        while not self._within_window(FILESYSTEM_WINDOWS):
            _logger.debug("Not in execution window; sleeping")
            time.sleep(60)
            
        sep_pos = filename.find('.')
        if sep_pos > -1:
            uid = filename[:sep_pos]
        else:
            uid = filename
            
        return database.record_exists(uid)
        

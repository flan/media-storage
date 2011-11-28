"""
Runs an asynchronous maintenance thread that handles deletions, compressions,
and bidirectional orphan-purging.
"""
import logging
import re
import threading
import time

from config import CONFIG
import compression
import database
import state

#Window structures to determine when threads may run
DELETION_WINDOWS = None
COMPRESSION_WINDOWS = None
DATABASE_WINDOWS = None
FILESYSTEM_WINDOWS = None

_logger = logging.getLogger("media_storage.maintainence")

def parse_windows():
    global DELETION_WINDOWS
    DELETION_WINDOWS = _parse_windows(CONFIG.maintainer_deletion_windows, 'deletion policy')
    global COMPRESSION_WINDOWS
    COMPRESSION_WINDOWS = _parse_windows(CONFIG.maintainer_compression_windows, 'compression policy')
    global DATABASE_WINDOWS
    DATABASE_WINDOWS = _parse_windows(CONFIG.maintainer_database_windows, 'database integrity')
    global FILESYSTEM_WINDOWS
    FILESYSTEM_WINDOWS = _parse_windows(CONFIG.maintainer_filesystem_windows, 'filesystem integrity')
    
def _parse_windows(definition, name):
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
    def __init__(self)
        _logger.info("Configuring %(name)s..." % {
         'name': self.name,
        })
        threding.Thread.__init__(self)
        self.daemon = True
        
    def self._within_window(self, windows):
        ts = time.localtime()
        ts = ts.tm_hour * 60 + ts.tm_min
        ranges = windows.get(ts.tm_wday)
        if not ranges:
            return False
            
        for (start, end) in ranges:
            if start <= ts < end:
                return True
        return False
        
class _PolicyMaintainer(_Maintainer):
    def run(self):
        while True:
            while not self._within_window(self._windows):
                _logger.debug("Not in execution window; sleeping")
                time.sleep(60)
                
            while True: #Process fixed records
                records_processed = False
                for record in database.enumerate_where({
                 self._fixed_field: {'$lt': int(time.time())},
                }):
                    _logger.info("Discovered fixed record: %(uid)s" % {
                     'uid': record['_id'],
                    })
                    records_processed = True
                    self._process_record(record)
                if not records_processed:
                    break
                    
            while True: #Process stale records
                records_processed = False
                for record in database.enumerate_where(self._stale_query % {
                 'time': int(time.time()),
                }):
                    _logger.info("Discovered stale record: %(uid)s" % {
                     'uid': record['_id'],
                    })
                    records_processed = True
                    self._process_record(record)
                if not records_processed:
                    break
                    
            _logger.debug("All records processed; sleeping")
            time.sleep(self._sleep_period)
            
class DeletionMaintainer(_PolicyMaintainer):
    """
    """
    name = 'deletion-maintainer'
    _stale_query = 'this.physical.atime + this.policy.delete.stale < %(time)i'
    _fixed_field = 'policy.delete.fixed'
    _sleep_period = CONFIG.maintainer_deletion_sleep
    _windows = DELETION_WINDOWS
    
    def _process_record(self, record):
        _logger.info("Deleting record '%(uid)s'..." % {
         'uid': record['_id'],
        })
        filesystem = state.get_filesystem(record['physical']['family'])
        try:
            filesystem.unlink(record)
        except Exception as e:
            #TODO: log
            pass
        else:
            database.drop_record(record['_id'])
            
class CompressionMaintainer(_PolicyMaintainer):
    """
    """
    name = 'compression-maintainer'
    _stale_query = 'this.physical.atime + this.policy.compress.stale < %(time)i'
    _fixed_field = 'policy.compress.fixed'
    _sleep_period = CONFIG.maintainer_compression_sleep
    _windows = COMPRESSION_WINDOWS
    
    def _process_record(self, record):
        _logger.info("Compressing record '%(uid)s'..." % {
         'uid': record['_id'],
        })
        current_compression = record['physical']['format'].get('comp')
        target_compression = record['policy']['compress'].get('comp')
        if current_compression == target_compression: #Nothing to do
            return
            
        filesystem = state.get_filesystem(record['physical']['family'])
        
        data = filesystem.get(record)
        if current_compression: #Must be decompressed first
            #log
            decompressor = getattr(compression, 'decompress_' + current_compression)
            data = decompressor(data)
        compressor = getattr(compression, 'compress_' + target_compression)
        data = compressor(data)
        
        old_format = record['physical']['format'].copy()
        record['physical']['format']['comp'] = target_compression
        try:
            filesystem.put(record, data)
        except Exception as e: #Harmless backout point
            #TODO: log
        else:
            record['policy']['compress'].clear() #Drop the compression policy
            try:
                database.update_record(record)
            except Exception as e: #Results in wasted space until the next attempt, but the old file will resolve
                #TODO: log
            else:
                record['physical']['format'] = old_format
                try:
                    filesystem.unlink(record)
                except Exception as e: #Results in wasted space, but non-fatal
                    #TODO: log
                    
class DatabaseMaintainer(_Maintainer):
    """
    """
    name = 'database-maintainer'
    
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
                    database.drop_record(record['_id'])
                    #TODO: log
                    
            if not records_retrieved: #Cycle complete
                _logger.debug("All records processed; sleeping")
                time.sleep(CONFIG.maintainer_database_sleep)
                ctime = -1.0
                
class FilesystemMaintainer(_Maintainer):
    """
    This thread should be disabled by default, since it would allow for the deletion of
    all data if the Mongo database is dropped for any reason, and, in smaller
    data-centres, a full filesystem backup may not exist.
    """
    name = 'filesystem-maintainer'
    
    def run(self):
        """
        Cycles through every filesystem entry in order, removing any files associated
        with database records that do not exist.
        """
        while True:
            for family in state.get_families():
                #TODO: log
                filesystem = state.get_filesystem(family)
                self._walk(filesystem, './')
                
            _logger.debug("All records processed; sleeping")
            time.sleep(CONFIG.maintainer_filesystem_sleep)
            
    def _walk(self, filesystem, path):
        try:
            for filename in filesystem.lsdir(path):
                subpath = path + filename
                if filesystem.is_dir(subpath):
                    self._walk(filesystem, subpath + '/')
                else:
                    try:
                        if not self._keep_file(filename):
                            filesystem.unlink(directory + filename)
                    except Exception as e:
                        #TODO: log
                        pass
        except Exception as e:
            #TODO: log
            pass
            
    def _keep_file(self, filename):
        while not self._within_window(FILESYSTEM_WINDOWS):
            _logger.debug("Not in execution window; sleeping")
            time.sleep(60)
            
        sep_pos = filename.find('.')
        if sep_pos > -1:
            uid = filename[:sep_pos]
        else:
            uid = filename
            
        return database.record_exists(uid)
        

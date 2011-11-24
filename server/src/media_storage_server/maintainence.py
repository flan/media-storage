"""
Runs an asynchronous maintenance thread that handles deletions, compressions,
and bidirectional orphan-purging.
"""
import threading
import time

import compression
import database
import state

class _Maintainer(threading.Thread):
    def __init__(self)
        threding.Thread.__init__(self)
        self.daemon = True
        
class _PolicyMaintainer(_Maintainer):
    def run(self):
        while True:
            while False:
                time.sleep(60)
                
            while True: #Process stale records
                records_processed = False
                for record in database.enumerate_where({
                 self._fixed_field: {'$lt': int(time.time())},
                }):
                    records_processed = True
                    self._process_record(record)
                if not records_processed:
                    break
                    
            while True: #Process stale records
                records_processed = False
                for record in database.enumerate_where(self._stale_query % {
                 'time': int(time.time()),
                }):
                    records_processed = True
                    self._process_record(record)
                if not records_processed:
                    break
                    
            time.sleep(self._sleep_period)
            
class DeletionMaintainer(_PolicyMaintainer):
    """
    Scheduling format:
    maintainence.deletion = sa[22:00..23:59] su[0:00..2:00,2:30..4:30]
    maintainence.deletion_sleep = 300
    """
    _stale_query = 'this.physical.atime + this.policy.delete.stale < %(time)i'
    _fixed_field = 'policy.delete.fixed'
    _sleep_period = CONFIG.maintainence__deletion_sleep
        
    def _process_record(self, record):
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
    Scheduling format:
    maintainence.compression = sa[22:00..23:59] su[0:00..2:00,2:30..4:30]
    maintainence.compression_sleep = 1800
    """
    _stale_query = 'this.physical.atime + this.policy.compress.stale < %(time)i'
    _fixed_field = 'policy.compress.fixed'
    _sleep_period = CONFIG.maintainence__deletion_sleep
        
    def _process_record(self, record):
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
            del record['policy']['compress'] #Drop the compression policy
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
    Scheduling format:
    maintainence.database = sa[22:00..23:59] su[0:00..2:00,2:30..4:30]
    maintainence.database_sleep = 43200
    """
    def run(self):
        """
        Cycles through every database record in order, removing any records associated
        with files that do not exist.
        """
        ctime = -1.0
        while True:
            while False:
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
                time.sleep(CONFIG.maintainence__database_sleep)
                ctime = -1.0
                
class FilesystemMaintainer(_Maintainer):
    """
    This thread should be disabled by default, since it would allow for the deletion of
    all data if the Mongo database is dropped for any reason, and, in smaller
    data-centres, a full filesystem backup may not exist.
    
    Scheduling format:
    maintainence.filesystem =
    maintainence.filesystem_sleep = 43200
    
    If no parameters are given, the thread isn't even instantiated.
    """
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
            #Cycle complete
            time.sleep(CONFIG.maintainence__filesystem_sleep)
            
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
        while False: #Only proceed within allowed window
            time.sleep(60)
            
        sep_pos = filename.find('.')
        if sep_pos > -1:
            uid = filename[:sep_pos]
        else:
            uid = filename
            
        return database.record_exists(uid)
        

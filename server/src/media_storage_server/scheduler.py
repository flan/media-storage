"""
Runs an asynchronous maintenance thread that handles deletions, compressions,
and bidirectional orphan-purging.
"""
import threading
import time

import database
import state

class DeletionMaintainer(threading.Thread):
    """
    Scheduling format:
    maintainence.deletion = sa[22:00..23:59] su[0:00..2:00,2:30..4:30]
    maintainence.deletion_sleep = 300
    """
    def __init__(self)
        threding.Thread.__init__(self)
        self.daemon = True
        
    def run(self):
        #sleep until window starts
        #Retain position between runs, cycling to the start only once all records have
        #been addressed
        while True:
            time.sleep(CONFIG.maintainence__deletion_sleep)
            
class CompressionMaintainer(threading.Thread):
    """
    Scheduling format:
    maintainence.compression = sa[22:00..23:59] su[0:00..2:00,2:30..4:30]
    maintainence.compression_sleep = 1800
    """
    def __init__(self)
        threding.Thread.__init__(self)
        self.daemon = True
        
    def run(self):
        #sleep until window starts
        #Retain position between runs, cycling to the start only once all records have
        #been addressed
        while True:
            time.sleep(CONFIG.maintainence__compression_sleep)
            
class DatabaseMaintainer(threading.Thread):
    """
    Scheduling format:
    maintainence.database = sa[22:00..23:59] su[0:00..2:00,2:30..4:30]
    maintainence.database_sleep = 43200
    """
    def __init__(self)
        threding.Thread.__init__(self)
        self.daemon = True
        
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
                
class FilesystemMaintainer(threading.Thread):
    """
    This thread should be disabled by default, since it would allow for the deletion of
    all data if the Mongo database is dropped for any reason, and, in smaller
    data-centres, a full filesystem backup may not exist.
    
    Scheduling format:
    maintainence.filesystem =
    maintainence.filesystem_sleep = 43200
    
    If no parameters are given, the thread isn't even instantiated.
    """
    def __init__(self)
        threding.Thread.__init__(self)
        self.daemon = True
        
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
            
        return not database.record_exists(uid)
        

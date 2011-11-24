"""
Runs an asynchronous maintenance thread that handles deletions, compressions,
and bidirectional orphan-purging.
"""
import threading
import time

import database
import state

class DeletionExecutor(threading.Thread):
    def run(self):
        #sleep until window starts
        #Retain position between runs, cycling to the start only once all records have
        #been addressed
        while True:
            time.sleep(60)
            
class CompressionExecutor(threading.Thread):
    def run(self):
        #sleep until window starts
        #Retain position between runs, cycling to the start only once all records have
        #been addressed
        while True:
            time.sleep(60)
            
class DatabasePurger(threading.Thread):
    def run(self):
        """
        Cycles through every database record in order, removing any records associated
        with files that do not exist.
        """
        #sleep until window starts
        #Retain position between runs, cycling to the start only once all records have
        #been addressed
        while True:
            time.sleep(60)
            
class FilesystemPurger(threading.Thread):
    def run(self):
        """
        Cycles through every filesystem entry in order, removing any files associated
        with database records that do not exist.
        """
        while True:
            for family in state.get_families():
                filesystem = state.get_filesystem(family)
                self._walk(filesystem, './')
                                
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
        

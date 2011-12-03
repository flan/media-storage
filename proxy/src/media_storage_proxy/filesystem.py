"""
Manages filesystem resources.
"""
import os
import Queue
import random
import threading

CONFIG = ''
CONFIG.upload_threads = 5

class Filesystem(object):
    _pool = None #A queue of files to be uploaded
    _threads = None
    
    def __init__(self):
        self._pool = Queue.Queue()
        self._threads = tuple((_Uploader(self) for i in range(CONFIG.upload_threads)))
        
        self._populate_pool()
        
        for thread in self._threads:
            thread.start()
            
    def _populate_pool(self):
        """
        Compiles a single list of all entities found in all server directories.
        The list is then shuffled and fed into self._pool.
        
        If any entity is missing its '.meta' file, the entity, along with any
        '.meta.part' file, is removed because it was not fully transferred before a
        crash.
        """
        
    def add_entity(self, path, meta):
        """
        Copies the file at the given path to the appropriate local path and adds a
        '.meta' file (which is written as '.meta.part', then renamed to avoid
        partial hits). On completion, the entity is added to the runtime upload pool.
        
        The entity is '.part'-cycled, too.
        """
        
    def upload_success(self, entity):
        pass
        
    def upload_failure(self, entity):
        pass
        
class _Uploader(threading.Thread):
    _filesystem = None #The filesystem entity to which the thread belongs
    
    def __init__(self, filesystem):
        threading.Thread.__init__(self)
        self.daemon = True
        
        self._filesystem = filesystem
        
    def run(self):
        """
        Gets the next entity from the filesystem's queue and attempts to upload it,
        informing the filesystem of success (removing the files) or failure (re-queuing
        the entity).
        """
        

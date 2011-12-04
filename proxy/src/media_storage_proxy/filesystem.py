"""
Manages filesystem resources.
"""
import os
import Queue
import random
import threading

import media_storage

from config import CONFIG

_pool = Queue.Queue() #A queue of files to be uploaded

class _Uploader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        
    def run(self):
        """
        Gets the next entity from the queue and attempts to upload it,
        informing the controller of success (removing the files) or failure (re-queuing
        the entity).
        """
        
def add_entity(path, meta):
    """
    Copies the file at the given path to the appropriate local path and adds a
    '.meta' file (which is written as '.meta.part', then renamed to avoid
    partial hits). On completion, the entity is added to the runtime upload pool.
    
    The entity is '.part'-cycled, too.
    """
    
def upload_success(entity):
    pass
    
def upload_failure(entity):
    pass
    
def _populate_pool():
    """
    Compiles a single list of all entities found in all server directories.
    The list is then shuffled and fed into self._pool.
    
    If any entity is missing its '.meta' file, the entity, along with any
    '.meta.part' file, is removed because it was not fully transferred before a
    crash.
    """

#Module setup
####################################################################################################
_threads = tuple((_Uploader() for i in range(CONFIG.upload_threads)))

_populate_pool()

for thread in _threads:
    thread.start()
    

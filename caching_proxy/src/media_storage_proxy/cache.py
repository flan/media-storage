"""
Manages cache resources.
"""
import os
import threading
import time
import traceback

import media_storage

from config import CONFIG
import mail

#Apply compression algorithm limiting
import media_storage.compression as compression
compression.SUPPORTED_FORMATS = tuple(config.compression_formats.intersection(compression.SUPPORTED_FORMATS))
del compression

_cache_lock = threading.Lock()
_cache = set() #Contains tuples of expiration times and paths; when an expiration is extended, the tuple is re-added

class _Purger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        
    def run(self):
        """
        Iterates over `_cache`, removing any files that have expired.
        """
        while True:
            current_time = int(time.time())
            dead_elements = []
            with _cache_lock as lock:
                for element in _cache:
                    (expiration, refresh_expiration, path) = element
                    if min(expiration, refresh_expiration) <= current_time:
                        try:
                            #remove file
                        except Exception as e:
                            ???
                        dead_elements.append(element)
                    else:
                        break 
                _cache.difference_update(dead_elements)
            time.sleep(5)
            
def _download(server, uid, read_key):
    #If file exists, validate read_key
    #Else, try to download meta and file, storing the result in cache
    #Retain expirations as ints
    
def get(server, uid, read_key):
    #Try _download, then return the file or None for a 404
    #If the file already exists and it has a '_cache:refresh' attribute, remove the old tuple and
    #add a new one with the current time + that number
    
def describe(server, uid, read_key):
    #Try _download, then return meta or None for a 404
    
def _clear_pool(self):
    """
    Removes all cached files on startup.
    """
    
#Module setup
####################################################################################################
_purger = _Purger()
_purger.start()


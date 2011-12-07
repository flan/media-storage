"""
Manages cache resources.
"""
import json
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

_EXTENSION_PARTIAL = '.' + CONFIG.storage_partial_extension
_EXTENSION_METADATA = '.' + CONFIG.storage_metadata_extension

_cache_lock = threading.Lock()
_cache = [] #Contains tuples of expiration times and paths

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
            with _cache_lock as lock:
                _cache.sort()
                for (i, (expiration, (contentfile, metafile))) in enumerate(_cache):
                    if expiration <= current_time:
                        for file in (contentfile, metafile,):
                            try:
                                os.unlink(file)
                            except Exception as e:
                                _logger.error("Unable to unlink %(path)s: %(error)s" % {
                                 'path': path,
                                 'error': str(e),
                                })
                    else:
                        cache = cache[i+1:]
                        break
            time.sleep(5)
            
def _download(host, port, uid, read_key, contentfile, metafile):
    client = media_storage.Client(host, port)
    with open(contentfile, 'wb') as cf:
        client.get(uid, read_key, output_file=cf, decompress_on_server=False, timeout=CONFIG.rules_timeout)
    with open(metafile, 'wb') as mf:
        meta = client.describe(uid, read_key, timeout=CONFIG.rules_timeout)
        meta['keys']['read'] = read_key
        mf.write(json.dumps(meta))
        
    _cache.append((
     min(CONFIG.rules_cache_max_time, max(CONFIG.rules_cache_min_time, meta['meta'].get('_cache:ttl', 0))),
     (contentfile, metafile)
    ))
    
def _retrieve(host, port, uid, read_key):
    target_path = "%(base)s%(host)s_%(port)i%(sep)s" % {
     'base': CONFIG.storage_path,
     'host': host,
     'port': port,
     'sep': os.path.sep,
    }
    try:
        if not os.path.isdir(target_path):
            _logger.info("Creating directory %(path)s..." % {
             'path': target_path,
            })
            try:
                os.path.makedirs(target_path, 0700)
            except OSError as e:
                if e.errno == 17:
                    _logger.debug("Directory %(path)s already exists" % {
                     'path': target_path,
                    })
                else:
                    raise
                    
        contentfile = "%(path)s%(name)s" % {
         'path': target_path,
         'name': meta['uid'],
        }
        metafile = "%(contentfile)s%(ext)s" % {
         'contentfile': contentfile,
         'ext': _EXTENSION_METADATA,
        }
        for file in (contentfile, metafile):
            if not os.path.isfile(file):
                _download(host, port, uid, read_key, contentfile, metafile)
                break
                
        mf = open(metafile, 'rb')
        meta = json.loads(mf.read())
        mf.close()        
    except (OSError, IOError):
        summary = "Unable to write files to disk; stack trace follows:\n" + traceback.format_exc()
        _logger.critical(summary)
        mail.send_alert(summary)
    else:
        if meta['keys']['read'] == read_key:
            return (contentfile, meta)
    return (None, None)
    
def get(host, port, uid, read_key):
    with _cache_lock as lock:
        (file, meta) = _retrieve(host, port, uid, read_key)
        if file:
            try:
                with open(file, 'rb') as content:
                    return (meta['physical']['format']['mime'], content.read())
            except Exception as e:
                summary = "Unable to read files from disk; stack trace follows:\n" + traceback.format_exc()
                _logger.critical(summary)
                mail.send_alert(summary)
        return None
        
def describe(host, port, uid, read_key):
    with _cache_lock as lock:
        (file, meta) = _retrieve(host, port, uid, read_key)
        return meta
        
def _clear_pool(self):
    """
    Removes all cached files on startup.
    """
    
#Module setup
####################################################################################################
_purger = _Purger()
_purger.start()


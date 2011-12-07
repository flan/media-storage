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
                        for file in (contentfile, metafile):
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
            time.sleep(CONFIG.storage_purge_interval)
            
def _download(host, port, uid, read_key, contentfile, metafile):
    client = media_storage.Client(host, port)
    with open(contentfile, 'wb') as cf:
        client.get(uid, read_key, output_file=cf, decompress_on_server=False, timeout=CONFIG.rules_timeout)
    with open(metafile, 'wb') as mf:
        meta = client.describe(uid, read_key, timeout=CONFIG.rules_timeout)
        meta['keys']['read'] = read_key
        mf.write(json.dumps(meta))
        
    with _cache_lock as lock:
        _cache.append((
         min(CONFIG.rules_cache_max_time, max(CONFIG.rules_cache_min_time, meta['meta'].get('_cache:ttl', 0))),
         (contentfile, metafile)
        ))
        
def _retrieve(host, port, uid, read_key, content):
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
        
        _cache_lock.acquire()
        try:
            for file in (contentfile, metafile):
                if not os.path.isfile(file):
                    _cache_lock.release()
                    _download(host, port, uid, read_key, contentfile, metafile)
                    _cache_lock.acquire()
                    break
                    
            mf = open(metafile, 'rb')
            meta = json.loads(mf.read())
            mf.close()
            if meta['keys']['read'] == read_key:
                if content:
                    cf = open(contentfile, 'rb')
                    content = cf.read()
                    cf.close()
                    return (content, meta)
                else:
                    return meta
            else:
                raise PermissionsError("Invalid read key provided for '%(uid)s'" % {
                 'uid': uid,
                })
        finally:
            try:
                _cache_lock.release()
            except Exception: #Lock alredy released
                pass
    except media_storage.NotAuthorisedError:
        raise PermissionsError("Invalid read key provided for '%(uid)s'" % {
         'uid': uid,
        })
    except (OSError, IOError):
        summary = "Unable to access files on disk; stack trace follows:\n" + traceback.format_exc()
        _logger.critical(summary)
        mail.send_alert(summary)
    return None
    
def get(host, port, uid, read_key):
    result = _retrieve(host, port, uid, read_key)
    if result:
        (content, meta) = result
        return (meta['physical']['format']['mime'], content)
    return None
    
def describe(host, port, uid, read_key):
    return _retrieve(host, port, uid, read_key)
    
def _clear_pool(self):
    """
    Removes all cached files on startup.
    """
    for (basedir, dirnames, filenames) in os.walk(CONFIG.storage_path):
        for filename in (basedir + f for f in filenames):
            _logger.info("Unlinking old cached file %(filename)s..." % {
             'filename': filename,
            })
            try:
                os.unlink(filename)
            except Exception as e:
                _logger.error("Unable to unlink cached file %(filename)s" % {
                 'filename': filename,
                })
                
#Module setup
####################################################################################################
_purger = _Purger()
_purger.start()


class PermissionsError(Exception):
    """
    Indicates that the given key does not grant permission to access the requested content.
    """
    

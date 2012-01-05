"""
Manages cache resources.
"""
import json
import logging
import os
import threading
import time
import traceback

import media_storage

from config import CONFIG
import mail

#Apply compression algorithm limiting
import media_storage.compression as compression
compression.SUPPORTED_FORMATS = tuple(CONFIG.compression_formats.intersection(compression.SUPPORTED_FORMATS))
del compression

_EXTENSION_METADATA = '.' + CONFIG.storage_metadata_extension

_cache_lock = threading.Lock()
_cache = [] #Contains tuples of expiration times and paths

_logger = logging.getLogger('media_storage.cache')

class _Purger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        
        _logger.info("Set up cache-purging thread")
        
    def run(self):
        """
        Iterates over `_cache`, removing any files that have expired.
        """
        global _cache
        while True:
            current_time = int(time.time())
            with _cache_lock:
                _cache.sort()
                for (i, (expiration, (contentfile, metafile))) in enumerate(_cache):
                    if expiration <= current_time:
                        for path in (contentfile, metafile):
                            _logger.info("Unlinking expired cached file %(path)s..." % {
                             'path': path,
                            })
                            try:
                                os.unlink(path)
                            except Exception as e:
                                _logger.error("Unable to unlink %(path)s: %(error)s" % {
                                 'path': path,
                                 'error': str(e),
                                })
                    else:
                        _cache = _cache[i + 1:]
                        break
                else: #Everything was expired
                    _cache = _cache[:0]
            time.sleep(CONFIG.storage_purge_interval)
            
def _download(host, port, uid, read_key, contentfile, metafile):
    client = media_storage.Client(host, port)
    with open(contentfile, 'wb') as cf:
        client.get(uid, read_key, output_file=cf, decompress_on_server=False, timeout=CONFIG.rules_timeout)
    with open(metafile, 'wb') as mf:
        meta = client.describe(uid, read_key, timeout=CONFIG.rules_timeout)
        meta['keys'] = {'read': read_key,}
        mf.write(json.dumps(meta))
        
    with _cache_lock:
        _cache.append((
         min(CONFIG.rules_max_cache_time, max(CONFIG.rules_min_cache_time, meta['meta'].get('_cache:ttl', 0))),
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
                os.makedirs(target_path, 0700)
            except OSError as e:
                if e.errno == 17:
                    _logger.debug("Directory %(path)s already exists" % {
                     'path': target_path,
                    })
                else:
                    raise
                    
        contentfile = "%(path)s%(name)s" % {
         'path': target_path,
         'name': uid,
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
    result = _retrieve(host, port, uid, read_key, True)
    if result:
        (content, meta) = result
        
        attributes = {}
        if 'ext' in meta['physical']['format']:
            attributes['_ext'] = meta['physical']['format']['ext']
        for (key, value) in meta['meta'].items():
            if key.startswith('_file:'):
                attributes[key[6:]] = value
                
        return (meta['physical']['format']['mime'], content, attributes)
    return None
    
def describe(host, port, uid, read_key):
    return _retrieve(host, port, uid, read_key, False)
    
def _clear_pool():
    """
    Removes all cached files on startup.
    """
    for (basedir, dirnames, filenames) in os.walk(CONFIG.storage_path):
        for filename in (basedir + os.path.sep + f for f in filenames):
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
def setup():
    _clear_pool()
    _Purger().start()
    
    
class PermissionsError(Exception):
    """
    Indicates that the given key does not grant permission to access the requested content.
    """
    

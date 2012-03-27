"""
Manages filesystem resources.
"""
import json
import logging
import os
import Queue
import random
import shutil
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

_EXTENSION_PARTIAL = '.' + CONFIG.storage_partial_extension
_EXTENSION_METADATA = '.' + CONFIG.storage_metadata_extension

_pool = Queue.Queue() #A queue of files to be uploaded
_flood_lock = threading.Lock() #A lock used to prevent concurrent accesses to the flooded-server collection
_flooded_servers = {} #A dictionary of servers considered overloaded, along with the time at which they'll be retried
_FLOOD_TIMEOUT = 2.5 #The amount of time to wait before re-attempting uploads against a flooded server, in seconds

_logger = logging.getLogger('media_storage.filesystem')

class _Uploader(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        
        _logger.info("Uploading thread created")
        
    def _close_file(self, data, path):
        try:
            data.close()
        except Exception:
            _logger.warn("Unable to close filehandle for %(file)s" % {
             'file': path,
            })
            
    def run(self):
        """
        Gets the next entity from the queue and attempts to upload it,
        informing the controller of success (removing the files) or failure (re-queuing
        the entity).
        """
        while True:
            _logger.debug("Upload thread waiting for task...")
            ((host, port), contentfile, metafile) = entity = _pool.get()
            with _flood_lock:
                server = (host, port)
                timeout = _flooded_servers.get(server)
                if timeout:
                    if timeout < time.time():
                        del _flooded_servers[server]
                    else:
                        _logger.debug("Record retrieved is associated with a flooded server and will be re-queued")
                        _upload_failure(entity)
                        continue
            client = media_storage.Client(host, port)
            
            try:
                _logger.debug("Loading metadata from '%(f)s'..." % {
                 'f': metafile,
                })
                metafile = open(metafile, 'rb')
                metadata = json.loads(metafile.read())
                metafile.close()
                
                _logger.debug("Loading content from '%(f)s'..." % {
                 'f': contentfile,
                })
                data = open(contentfile, 'rb')
                
                _logger.info("Uploading '%(uid)s'..." % {
                 'uid': metadata['uid'],
                })
                client.put(
                 data, metadata['physical']['format']['mime'], family=metadata['physical']['family'],
                 comp=metadata['physical']['format']['comp'], compress_on_server=False,
                 deletion_policy=metadata['policy']['delete'], compression_policy=metadata['policy']['compress'],
                 meta=metadata['meta'],
                 uid=metadata['uid'], keys=metadata['keys'],
                 timeout=CONFIG.upload_timeout
                )
            except media_storage.InvalidRecordError:
                self._close_file(data, contentfile) #Must be done here, since Microsoft filesystems don't support unlinking open files
                _logger.error("The entity '%(uid)s' was submitted with invalid metadata and cannot be uploaded; its files will be unlinked" % {
                 'uid': metadata['uid'],
                })
                _upload_success(entity)
            except Exception as e:
                self._close_file(data, contentfile) #Done here for consistency, since Microsoft filesystems don't support unlinking open files
                _logger.error("An unexpected error occurred and the entity '%(uid)s' will be re-queued; traceback follows:\n%(traceback)s" % {
                 'uid': metadata['uid'],
                 'traceback': traceback.format_exc(),
                })
                _upload_failure(entity)
                with _flood_lock:
                    _flooded_servers[(host, port)] = time.time() + _FLOOD_TIMEOUT
            else:
                self._close_file(data, contentfile) #Must be done here, since Microsoft filesystems don't support unlinking open files
                _logger.info("The entity '%(uid)s' has been successfully uploaded and its files will be unlinked" % {
                 'uid': metadata['uid'],
                })
                _upload_success(entity)
                
def add_entity(host, port, path, meta):
    """
    Copies the file at the given path to the appropriate local path and adds a
    '.meta' file. On completion, the entity is added to the runtime upload pool.
    
    The entity is '.part'-cycled.
    """
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
                    
        permfile = "%(path)s%(name)s" % {
         'path': target_path,
         'name': meta['uid'],
        }
        tempfile = "%(permfile)s%(ext)s" % {
         'permfile': permfile,
         'ext': _EXTENSION_PARTIAL,
        }
        _logger.debug("Copying data from %(source)s to %(destination)s..." % {
         'source': path,
         'destination': tempfile,
        })
        shutil.copyfile(path, tempfile)
        
        metafile = "%(permfile)s%(ext)s" % {
         'permfile': permfile,
         'ext': _EXTENSION_METADATA,
        }
        _logger.debug("Writing metadata to %(destination)s..." % {
         'destination': metafile,
        })
        metafile_fp = open(metafile, 'wb')
        metafile_fp.write(json.dumps(meta))
        metafile_fp.close()
        
        _logger.debug("Renaming data from %(source)s to %(destination)s..." % {
         'source': tempfile,
         'destination': permfile,
        })
        os.rename(tempfile, permfile)
    except (OSError, IOError):
        summary = "Unable to write files to disk; stack trace follows:\n" + trceback.format_exc()
        _logger.critical(summary)
        mail.send_alert(summary)
    else:
        _pool.put(((host.encode('utf-8'), port), permfile.encode('utf-8'), metafile.encode('utf-8')))
        
def _upload_success(entity):
    ((host, port), contentfile, metafile) = entity
    for filename in (contentfile, metafile):
        _logger.debug("Unlinking uploaded entity %(f)s..." % {
         'f': filename,
        })
        try:
            os.unlink(filename)
        except Exception as e:
            _logger.warn("Unable to unlink %(f)s: %(error)s" % {
             'f': filename,
             'error': str(e),
            })
            
def _upload_failure(entity):
    _pool.put(entity)
    
def _populate_pool():
    """
    Compiles a single list of all entities found in all server directories.
    The list is then shuffled and fed into self._pool.
    
    If any entity is missing its '.meta' file or is in a '.part' state, the entity, along with any
    '.meta' file, is removed because it was not fully transferred before a crash.
    """
    entities = []
    for directory in (d for d in os.listdir(CONFIG.storage_path) if os.path.isdir(os.path.join(CONFIG.storage_path, d))):
        try:
            (host, port) = directory.rsplit('_', 1)
            port = int(port)
            directory = os.path.join(CONFIG.storage_path, directory) + os.path.sep
        except Exception as e:
            _logger.warn("Invalid directory; does not imply a server address: %(root)s/%(dirname)s" % {
             'root': CONFIG.storage_path,
             'dirname': dirname,
            })
        else:
            #Remove partial files
            for filename in (directory + f for f in os.listdir(directory) if f.endswith(_EXTENSION_PARTIAL)):
                _logger.info("Unlinking partial entity %(f)s..." % {
                 'f': filename,
                })
                try:
                    os.unlink(filename)
                except Exception as e:
                    _logger.warn("Unable to unlink partial file %(f)s: %(error)s" % {
                     'f': filename,
                     'error': str(e),
                    })
                    
            for filename in (directory + f for f in os.listdir(directory) if not '.' in f):
                if not os.path.isfile("%(base)s%(ext)s" % {
                 'base': filename,
                 'ext': _EXTENSION_METADATA,
                }):
                    _logger.info("Unlinking metadata-less entity %(f)s..." % {
                     'f': filename,
                    })
                    try:
                        os.unlink(filename)
                    except Exception as e:
                        _logger.warn("Unable to unlink metadata-missing file %(f)s: %(error)s" % {
                         'f': filename,
                         'error': str(e),
                        })
                else: #Add the file to the upload queue
                    _logger.info("Registered entity %(f)s" % {
                     'f': filename,
                    })
                    entities.append(((host, port), filename, filename + _EXTENSION_METADATA))
                    
    random.shuffle(entities)
    for entity in entities:
        _pool.put(entity)
        
#Module setup
####################################################################################################
def setup():
    _populate_pool()
    
    for thread in (_Uploader() for i in range(CONFIG.upload_threads)):
        thread.start()
        

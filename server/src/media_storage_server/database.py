"""
Provides all necessary database-access routines and query-interpretation.
"""
import logging
import types

import pymongo

from config import CONFIG

_CREDENTIALS = CONFIG.database_credentials
_CONNECTION = None
if CONFIG.database_address[1]:
    _CONNECTION = pymongo.Connection(*CONFIG.database_address)
else:
    _CONNECTION = pymongo.Connection(CONFIG.database_address[0])
_DATABASE = _CONNECTION[CONFIG.database_database]
_COLLECTION = _DATABASE[CONFIG.database_collection]

for index in (
 'physical.family', 'physical.ctime', 'physical.atime',
 'policy.delete.fixed', 'policy.delete.stale',
 'policy.compress.fixed', 'policy.compress.stale',
):
    _COLLECTION.ensure_index(index)
    
_logger = logging.getLogger("media_storage.database")

def authenticate(f):
    def authenticated_f(*args, **kwargs):
        if _CREDENTIALS:
            _logger.debug("Authenticating to database...")
            _DATABASE.authenticate(*_CREDENTIALS)
        return f(*args, **kwargs)
    return authenticated_f
    
@authenticate
def enumerate_all(ctime):
    return _COLLECTION.find(
     spec={
      'physical.ctime': {'$gt': ctime,},
     },
     fields=['physical'],
     limit=250,
     sort=[('physical.ctime', pymongo.ASCENDING)],
    )
    
@authenticate
def enumerate_where(query):
    if type(query) in types.StringTypes:
        return _COLLECTION.find(
         spec={'$where': query},
        )
    else:
        return _COLLECTION.find(
         spec=query,
        )
        
@authenticate
def enumerate_meta():
    """
    The client query interface.
    """
    
    #Apply the following to the web request
    #del record['physical']['minRes']
    #del record['key']
    
@authenticate
def get_record(uid):
    _logger.debug("Retrieving record for '%(uid)s'" % {
     'uid': uid,
    })
    record = _COLLECTION.find_one(uid)
    if record is None:
        _logger.info("No record found for '%(uid)s'" % {
         'uid': uid,
        })
    return record
    
@authenticate
def add_record(record):
    _logger.info("Adding record for '%(uid)s'..." % {
     'uid': record['_id'],
    })
    _COLLECTION.insert(record)
    
@authenticate
def drop_record(uid):
    _COLLECTION.remove(uid)
    
@authenticate
def record_exists(uid):
    return bool(_COLLECTION.find_one(
     spec=uid,
     fields=[],
    ))
    

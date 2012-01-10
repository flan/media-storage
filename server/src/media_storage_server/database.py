"""
media-storage.database
======================

Provides all necessary database-access routines and query-execution logic.

Legal
+++++
 This file is part of media-storage.
 media-storage is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 
 (C) Neil Tallim, 2012 <flan@uguu.ca>
"""
import logging

import pymongo

from config import CONFIG

_CREDENTIALS = CONFIG.database_credentials
_CONNECTION = None
if CONFIG.database_address[1]: #Connect with an explicit port
    _CONNECTION = pymongo.Connection(*CONFIG.database_address)
else: #Connect with the default port
    _CONNECTION = pymongo.Connection(CONFIG.database_address[0])
_DATABASE = _CONNECTION[CONFIG.database_database]
_COLLECTION = _DATABASE[CONFIG.database_collection]

for index in ( #Ensure that indexes exist on all important attributes
 'physical.family', 'physical.ctime', 'physical.atime',
 'policy.delete.fixed', 'policy.delete.stale',
 'policy.compress.fixed', 'policy.compress.stale',
):
    _COLLECTION.ensure_index(index)
    
_logger = logging.getLogger("media_storage.database")

def authenticate(f):
    """
    A decorator that ensures the active thread has authenticated to the Mongo database, if
    credentials were supplied.
    """
    def authenticated_f(*args, **kwargs):
        if _CREDENTIALS:
            _logger.debug("Authenticating to database...")
            try:
                _DATABASE.authenticate(*_CREDENTIALS)
            except Exception as e:
                _logger.error("Unable to authenticate to database: %(error)s" % {
                 'error': str(e),
                })
                raise
        return f(*args, **kwargs)
    return authenticated_f
    
@authenticate
def list_families():
    """
    Enumerates every family defined in the database, as a list of strings.
    """
    try:
        return _COLLECTION.distinct('physical.family')
    except Exception as e:
        _logger.error("Unable to enumerate families: %(error)s" % {
         'error': str(e),
        })
        raise
        
@authenticate
def enumerate_all(ctime, limit=250):
    """
    Iterates over every record in the database, using `ctime` as a query-range indicator; `ctime`
    should be the last timestamp returned in the previous call, or 0 for the first invocation.
    
    Up to `limit`=250 records are returned as a list.
    """
    try:
        return _COLLECTION.find(
         spec={
          'physical.ctime': {'$gt': ctime,},
         },
         fields=['physical'],
         limit=limit,
         sort=[('physical.ctime', pymongo.ASCENDING)],
        )
    except Exception as e:
        _logger.error("Unable to retrieve records: %(error)s" % {
         'error': str(e),
        })
        raise
        
@authenticate
def enumerate_where(query):
    """
    Returns all records that match `query`, a Mongo query structure, up to a system-configured
    limit, as a list. To enumerate all possible matches, ctimes can be used to build range windows.
    """
    try:
        return _COLLECTION.find(
         spec=query,
         limit=CONFIG.security_query_size,
         sort=[('physical.ctime', pymongo.ASCENDING)],
        )
    except Exception as e:
        _logger.error("Unable to retrieve records: %(error)s" % {
         'error': str(e),
        })
        raise
        
@authenticate
def get_record(uid):
    """
    Returns the record associated with the given `uid`, or None if no record exists.
    """
    _logger.debug("Retrieving record for '%(uid)s'..." % {
     'uid': uid,
    })
    try:
        record = _COLLECTION.find_one(uid)
    except Exception as e:
        _logger.error("Unable to retrieve record: %(error)s" % {
         'error': str(e),
        })
        raise
    else:
        if record is None:
            _logger.info("No record found for '%(uid)s'" % {
             'uid': uid,
            })
        return record
        
@authenticate
def add_record(record):
    """
    Adds `record` to the database, assuming it is well-formed on insertion.
    """
    _logger.info("Adding record for '%(uid)s'..." % {
     'uid': record['_id'],
    })
    try:
        _COLLECTION.insert(record)
    except Exception as e:
        _logger.error("Unable to add record: %(error)s" % {
         'error': str(e),
        })
        raise
        
@authenticate
def update_record(record):
    """
    Updates `record` in the database, assuming it is well-formed.
    """
    _logger.info("Updating record for '%(uid)s'..." % {
     'uid': record['_id'],
    })
    try:
        _COLLECTION.update({'_id': record['_id']}, record)
    except Exception as e:
        _logger.error("Unable to update record: %(error)s" % {
         'error': str(e),
        })
        raise
        
@authenticate
def drop_record(uid):
    """
    Removes the record associated with `uid` from the database, if it exists.
    """
    _logger.info("Dropping record for '%(uid)s'..." % {
     'uid': uid,
    })
    try:
        _COLLECTION.remove(uid)
    except Exception as e:
        _logger.error("Unable to remove record: %(error)s" % {
         'error': str(e),
        })
        raise
        
@authenticate
def record_exists(uid):
    """
    Provides a boolean value indicating whether a record exists for `uid`.
    """
    _logger.debug("Testing existence of record for '%(uid)s'..." % {
     'uid': uid,
    })
    try:
        return bool(_COLLECTION.find_one(
         spec=uid,
         fields=[],
        ))
    except Exception as e:
        _logger.error("Unable to search for record: %(error)s" % {
         'error': str(e),
        })
        raise
        

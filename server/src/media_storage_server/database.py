"""
Provides all necessary database-access routines and query-interpretation.
"""
import types

def enumerate_all(ctime):
    return db.collection.find(
     spec={
      'physical.ctime': {'$gt': ctime,},
     },
     fields=['physical'],
     limit=250,
     sort=[('physical.ctime', pymongo.ASCENDING)],
    )
    
def enumerate_where(query):
    if type(query) in types.StringTypes:
        return db.collection.find(
         spec={'$where': query},
        )
    else:
        return db.collection.find(
         spec=query,
        )
        
def enumerate_meta():
    """
    The client query interface.
    """
    
    
    #Apply the following to the web request
    #del record['physical']['minRes']
    
def get_record(uid):
    return db.collection.find_one(uid)
    
def add_record(record):
    db.collection.insert(record)
    
def drop_record(uid):
    db.collection.remove(uid)
    
def record_exists(uid):
    return bool(db.collection.find_one(
     spec=uid,
     fields=[],
    ))
    

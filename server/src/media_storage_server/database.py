"""
Provides all necessary database-access routines and query-interpretation.
"""

def enumerate_all(ctime):
    return db.collection.find(
     spec={
      'physical.ctime': {'$gt': ctime,},
     },
     fields=['physical'],
     limit=250,
     sort=[('physical.ctime', pymongo.ASCENDING)],
    )
    
def drop_record(uid):
    db.collection.remove(uid)
    
def record_exists(uid):
    return bool(db.collection.find_one(
     spec=uid,
     fields=[],
    ))
    

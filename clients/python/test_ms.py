import time

import media_storage

print "Storing file..."
x = media_storage.Client('localhost', 43001)
#y = x.put(open('/home/flan/x.wav'), 'audio/x-wav')
y = x.put(open('/home/flan/Music/Gust Sound Team - Ar tonelico III (hymmnos blue)/04_EXEC_FLIP_ARPHAGE-..ogg'), 'application/ogg', extension='ogg',
 compression_policy={
  'stale': 5,
  'comp': 'bz2',
 },
 deletion_policy={
  'fixed': 300,
 },
)
print(repr(y))
print

print "Retrieving storage record..."
print(repr(x.describe(y['uid'], y['keys']['read'])))
print

print "Retrieving content..."
(mime, handle) = x.get(y['uid'], y['keys']['read'])
print "Mime: " + mime
print "Content: " + (open('/home/flan/x.wav').read() == handle.read() and 'match' or 'non-match')
print

print "Updating metadata..."
x.update(y['uid'], y['keys']['write'], new={
 'instruments': 'electric-violin',
 'different': 'very',
})
print

print "Retrieving storage record..."
print(repr(x.describe(y['uid'], y['keys']['read'])))
print

query = media_storage.QueryStruct()
query.meta['green'] = 5
print "Querying for matches ('green' = 5)..."
print(repr(x.query(query)))
print

print "Unlinking entity..."
#x.unlink(y['uid'], y['keys']['write'])
print

print "Querying for matches ('green' = 5)..."
print(repr(x.query(query)))
print

print "Done"


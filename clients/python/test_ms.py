import media_storage

print "Storing file..."
x = media_storage.Client('http://localhost:1234/')
y = x.put(open('/home/flan/x.txt'), 'audio/x-wav')
print(repr(y))
print

print "Retrieving storage record..."
print(repr(x.describe(y['uid'], y['keys']['read'])))
print

print "Retrieving content..."
(mime, handle) = x.get(y['uid'], y['keys']['read'])
print "Mime: " + mime
print "Content: " + (open('/home/flan/x.txt').read() == handle.read() and 'match' or 'non-match')
print

print "Updating metadata..."
x.update(y['uid'], y['keys']['write'], new={
 'hello': 'goodbye',
 'green': 5,
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
x.unlink(y['uid'], y['keys']['write'])
print

print "Querying for matches ('green' = 5)..."
print(repr(x.query(query)))
print

print "Done"


import json
import urllib2

js = {
 'physical': {
  'family': 'taco',
  'format': {
   'mime': 'whee',
   'ext': 'desu',
   'comp': 'bz2',
  },
 },
 'meta': {
  'dance': True,
 },
}

data = "Hello, world!"

request = urllib2.Request(
 'http://localhost:1234/put',
 headers={
  'Media-Storage-Compress-On-Server': 'yes',
 },
)
record_pointer = urllib2.urlopen(
 request,
 data=(json.dumps(js) + '\0' + data),
).read()

request = urllib2.Request(
 'http://localhost:1234/describe',
 headers={
 },
)
record_full = urllib2.urlopen(
 request,
 data=(record_pointer),
).read()

print record_full

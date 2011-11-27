import json
import urllib2

js = {
 'physical': {
  'family': 'taco',
  'format': {
   'mime': 'text/plain',
   'ext': 'txt',
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
print urllib2.urlopen(
 request,
 data=(record_pointer),
).read()

request = urllib2.Request(
 'http://localhost:1234/get',
 headers={
  'Media-Storage-Supported-Compression': 'gzip;lzma',
 },
)
response = urllib2.urlopen(
 request,
 data=(record_pointer),
)
print response.headers
print response.read()


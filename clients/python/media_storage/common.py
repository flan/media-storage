"""
media_storage.common
====================

Defines shared methods, like HTTP accessors, and classes, like exceptions and
data structures.

Usage
-----

This module is not meant to be used externally; relevant objects are exported
to the package level.

Legal
-----

This file is part of the LGPLed Python client of the media-storage project.
This package is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and
GNU Lesser General Public License along with this program. If not, see
<http://www.gnu.org/licenses/>.
 
(C) Neil Tallim, 2011
"""
import json
import mmap
import random
import sys
import tempfile
import types
import urllib2

try:
    import dns.resolver
except ImportError: #DNS is not available
    pass
    
#Server path constants
SERVER_PING = 'ping'
SERVER_LIST_FAMILIES = 'list/families'
SERVER_STATUS = 'status'
SERVER_PUT = 'put'
SERVER_GET = 'get'
SERVER_DESCRIBE = 'describe'
SERVER_UNLINK = 'unlink'
SERVER_UPDATE = 'update'
SERVER_QUERY = 'query'

#Request headers
HEADER_COMPRESS_ON_SERVER = 'Media-Storage-Compress-On-Server'
HEADER_COMPRESS_ON_SERVER_TRUE = 'yes'
HEADER_COMPRESS_ON_SERVER_FALSE = 'no' #Implied by omission
HEADER_SUPPORTED_COMPRESSION = 'Media-Storage-Supported-Compression'
HEADER_SUPPORTED_COMPRESSION_DELIMITER = ';'
#Response headers
HEADER_APPLIED_COMPRESSION = 'Media-Storage-Applied-Compression'
HEADER_CONTENT_TYPE = 'Content-Type'
#Response properties
PROPERTY_CONTENT_LENGTH = 'content-length'
PROPERTY_CONTENT_TYPE = 'content-type'
PROPERTY_APPLIED_COMPRESSION = 'applied-compression'
PROPERTY_FILE_ATTRIBUTES = 'file-attributes'

_CHUNK_SIZE = 32 * 1024 #Transfer data in 32k chunks

#Constants to expedite construction of multipart/formdata packets
_FORM_SEP = '--'
_FORM_BOUNDARY = '---...???,,,$$$RFC-1867-kOmPl1aNt-bOuNdArY$$$,,,???...---'
_FORM_CRLF = '\r\n'
_FORM_CONTENT_TYPE = 'multipart/form-data; boundary=' + _FORM_BOUNDARY
_FORM_HEADER = (_FORM_SEP + _FORM_BOUNDARY + _FORM_CRLF +
 'Content-Disposition: form-data; name="header"' + _FORM_CRLF * 2)
_FORM_PRE_CONTENT = (_FORM_CRLF + _FORM_SEP + _FORM_BOUNDARY + _FORM_CRLF +
 'Content-Disposition: form-data; name="content"; filename="payload"' + _FORM_CRLF +
 'Content-Type: application/octet-stream' + _FORM_CRLF +
 'Content-Transfer-Encoding: binary' + _FORM_CRLF * 2)
_FORM_FOOTER = _FORM_CRLF + _FORM_SEP + _FORM_BOUNDARY + _FORM_SEP + _FORM_CRLF

def _encode_multipart_formdata(header, content):
    """
    Assembles a multipart/formdata request, needed for some transfer methods.
    """
    temp = tempfile.SpooledTemporaryFile(10 * 1024 * 1024)
    temp.write(_FORM_HEADER)
    temp.write(header)
    temp.write(_FORM_PRE_CONTENT)
    if type(content) in types.StringTypes:
        temp.write(content)
    else:
        transfer_data(content, temp)
    temp.write(_FORM_FOOTER)
    temp.seek(0)
    return mmap.mmap(temp.fileno(), 0, access=mmap.ACCESS_READ)
    
def transfer_data(source, destination):
    """
    Reads every byte, in reasonable-sized chunks, from the file-like object `source` into the
    file-like object `destination`. No seeking occurs after the transfer is complete.
    
    The number of bytes transferred is returned.
    """
    size = 0
    while True:
        chunk = source.read(_CHUNK_SIZE)
        if not chunk:
            break
        destination.write(chunk)
        destination.flush()
        size += len(chunk)
    return size
    
def assemble_request(destination, header, headers={}, data=None):
    """
    `destination` is the URI to which the request will be sent.
    
    `header` is the JSON structure that contains the semantics of the request.
    
    `headers` is a dictionary containing any optional headers to be sent to the server, in addition
    to any required by the protocol (new headers will overwrite base ones).
    
    `data` is an optional file-like object containing additional binary content to be delivered with
    the request. It can also be a string, theoretically. Just sayin'.
    """
    base_headers = {
     'Content-Type': 'application/json',
    }
    base_headers.update(headers)
    
    body = json.dumps(header)
    if data:
        try:
            body = _encode_multipart_formdata(body, (
             (type(data) in types.StringTypes or type(data) is mmap.mmap) and data or
             mmap.mmap(data.fileno(), 0, access=mmap.ACCESS_READ)
            ))
        except MemoryError:
            raise MemoryError("Insufficient memory to buffer data for storage")
        base_headers['Content-Type'] = _FORM_CONTENT_TYPE
        
    return urllib2.Request(
     url=destination,
     headers=base_headers,
     data=body,
    )
    
def send_request(request, output=None, timeout=10.0):
    """
    Sends the assembled `request`, returning any interesting properties, and either adds the body as
    a string in a tuple or writes it to the specified `output` file-like object, seeking back to 0,
    returning only the properties.
    
    Default `timeout` is 10s.
    
    All ``ProtocolError`` sub-types, ``URLError``, or general ``Exception``s may be raised, as needed.
    """
    try:
        response = urllib2.urlopen(request, timeout=timeout)
    except urllib2.HTTPError as e:
        if e.code == 403:
            raise NotAuthorisedError("The requested operation could not be performed because an invalid key was provided")
        elif e.code == 404:
            raise NotFoundError("The requested resource was not retrievable; it may have been deleted or not yet defined")
        elif e.code == 409:
            raise InvalidRecordError("The uploaded request is structurally flawed and cannot be processed")
        elif e.code == 412:
            raise InvalidHeadersError("One or more of the headers supplied (likely Content-Length) was rejected by the server")
        elif e.code == 503:
            raise TemporaryFailureError("The server was unable to process the request")
        else:
            raise ProtocolError("Unable to send message; code: %(code)i" % {
             'code': e.code,
            })
    except urllib2.URLError as e:
        raise URLError("Unable to send message: %(error)s" % {
         'error': str(e),
        })
    except Exception:
        raise
    else:
        properties = {
         PROPERTY_APPLIED_COMPRESSION: response.headers.get(HEADER_APPLIED_COMPRESSION),
         PROPERTY_CONTENT_TYPE: response.headers.get(HEADER_CONTENT_TYPE),
        }
        if output:
            properties[PROPERTY_CONTENT_LENGTH] = transfer_data(response, output)
            output.seek(0)
            return properties
        try:
            return (properties, response.read())
        except MemoryError:
            raise MemoryError("Insufficient memory to buffer data from storage")
            
class QueryStruct(object):
    """
    The structure used to issue queries against a server.
    
    All attributes are meant to be set publically, though `meta` is a dictionary and should be
    treated as such, being populated with keys to check and values to match on, of appropriate
    types. Anything irrelevant should be left as `None`.
    
    To perform non-matching queries on metadata, the following filters may be used:
     - ':range:<min>:<max>' : range queries over numeric types, inclusive on both ends
     - ':lte:<number>'/':gte:<number>' : relative queries over numeric types
     - ':re:<pcre>'/':re.i:<pcre>' : PCRE regular expression, with the second form being
       case-insensitive
     - ':like:<pattern>' : behaves like SQL 'LIKE', with '%' as wildcards
     - ':ilike:<pattern>' : behaves like SQL 'ILIKE', with '%' as wildcards
     - '::<whatever>' : Ignores the first colon and avoids parsing, in case a value actually starts
       with a ':<filter>:' structure
       
    In addition to `meta`, the following fields are defined:
     - `ctime_min`/`ctime_max` : if either is set, it serves as an <=/>= check against ctime
     - `atime_min`/`atime_max` : if either is set, it serves as an <=/>= check against atime
     - `accesses_min`/`accesses_max` : if either is set, it serves as an <=/>= check against
       accesses
     - `family` : if set, performs an explicit match against family
     - `mime` : if set, if a '/' is present, performs an explicit match against MIME; otherwise,
       performs a match against the super-type of MIME
    """
    ctime_min = None #The minimum ctime (float) of records to enumerate
    ctime_max = None #The maximum ctime (float) of records to enumerate
    atime_min = None #The minimum atime (int) of records to enumerate
    atime_max = None #The maximum atime (int) of records to enumerate
    accesses_min = None #The minimum access-count (int) of records to enumerate
    accesses_max = None #The maximum access-count (int) of records to enumerate
    family = None #The family (string) of records to enumerate
    mime = None #The MIME-type (string; omitting '/' selects supertype) of records to enumerate
    meta = None #A dictionary of metadata to match, either literally or using provided filters, encoded as strings
    
    def __init__(self):
        """
        Initialises instance variables.
        """
        self.meta = {}
        
    def to_dict(self):
        """
        Renders the structure's data as a dictionary.
        """
        return {
         'ctime': {
          'min': self.ctime_min,
          'max': self.ctime_max,
         },
         'atime': {
          'min': self.atime_min,
          'max': self.atime_max,
         },
         'accesses': {
          'min': self.accesses_min,
          'max': self.accesses_max,
         },
         'family': self.family,
         'mime': self.mime,
         'meta': self.meta,
        }

class Server(object):
    """
    Describes the server-environment for data-storage.
    """
    _host = None #The host to which connections will be established; may be a name, IP, or SRV identifier
    _port = 0 #The port to which connections will be established; may be undefined if using SRV
    _ssl = False #True if SSL connections are to be used
    _srv = False #True if SRV lookups are to be performed against `_host`
    
    def __init__(self, host, port=0, ssl=False, srv=False):
        """
        `host` may be an address or IP; `port` is the port to which connections
        should be made, unless `srv` is set, which will cause the hostname to be
        looked up to resolve SRV records; these supply port information.

        If `ssl` is set, all communications will take place over HTTPS, which
        carries a substantial performance penalty for large files.
        """
        if not port and not srv:
            raise ValueError("Port may only be undefined when using SRV records")

        self._host = host
        self._port = (not srv and port) or 0
        self._ssl = ssl
        self._srv = srv

    def to_dictionary(self):
        """
        Provides all meaningful constructor parameters as a dictionary.
        """
        return {
         'host': self._host,
         'port': self._port,
         'ssl': self._ssl,
         'srv': self._srv,
        }

    def _assemble(self, host, port, ssl):
        """
        Provides a schema-complete address for a host.
        """
        return "http%(ssl)s://%(host)s:%(port)i/" % {
         'ssl': ssl and 's' or '',
         'host': host,
         'port': port,
        }

    def get_host(self):
        """
        Resolves a schema-complete address for a usable host or raises `URLError` if resolution
        fails.
        """
        if self._srv:
            candidates = {}
            try:
                for record in dns.resolver.query(self._host, 'SRV'):
                    container = candidates.get(record.priority)
                    if not container:
                        container = candidates[record.priority] = []
                    container.append(record)
            except Exception as e:
                raise URLError("Unable to resolve SRV record: %(error)s" % {
                 'error': str(e),
                })
                
            for (priority, container) in sorted(candidates.items()):
                while container:
                    choices = []
                    for choice in container:
                        choices += [choice] * choice.weight
                    candidate = random.choice(choices)

                    address = self._assemble(candidate.canonicalize().to_text()[:-1], candidate.port, self._ssl)
                    try: #Send a ping, just like the clients
                        request = assemble_request(address + SERVER_PING, {})
                        (properties, response) = send_request(request, timeout=1)
                        json.loads(response)
                    except Exception:
                        container.remove(candidate)
                    else:
                        return address
            else:
                raise URLError("No active servers found via SRV resolution")
        else:
            return self._assemble(self._host, self._port, self._ssl)
            
            
class Error(Exception):
    """
    The base class from which all errors native to this package inherit.
    """
    
class ProtocolError(Error):
    """
    Indicates a problem with the transport protocol, which is, at this point, only HTTP.
    """
    
class NotAuthorisedError(ProtocolError):
    """
    The server returned a 403.
    """
    
class NotFoundError(ProtocolError):
    """
    The server returned a 404.
    """
    
class NotPresentError(NotFoundError):
    """
    The server was unable to find the specified file, though records exist.
    """
    def __init__(self, json):
        NotFoundError.__init__(self, "Unable to find requested file, though records exist")
        self.json = json
        
class InvalidRecordError(ProtocolError):
    """
    The server returned a 409, meaning that the request is flawed.
    """
    
class InvalidHeadersError(ProtocolError):
    """
    The server returned a 412.
    """
    
class TemporaryFailureError(ProtocolError):
    """
    The server returned a 503.
    """
    
class URLError(Error):
    """
    Indicates an error with URL resolution.
    """
    

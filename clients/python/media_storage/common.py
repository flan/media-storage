"""
Shared functions and stuff. Mostly just HTTP access methods.
"""
import json
import types
import urllib2

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
PROPERTY_CONTENT_TYPE = 'content-type'
PROPERTY_APPLIED_COMPRESSION = 'applied-compression'

_CHUNK_SIZE = 32 * 1024 #Transfer data in 32k chunks

def transfer_data(source, destination):
    while True:
        chunk = source.read(_CHUNK_SIZE)
        if not chunk:
            break
        destination.write(chunk)
        destination.flush()
    destination.seek(0)

def assemble_request(destination, header, headers={}, data=None):
    """
    `destination` is the URI to which the request will be sent.
    
    `header` is the JSON structure that contains the semantics of the request.
    
    `headers` is a dictionary containing any optional headers to be sent to the server, in addition
    to any required by the protocol (new headers will overwrite base ones).
    
    `data` is an optional file-like object containing additional binary content to be delivered with
    the request. It is appended after the JSON header, delimited by a null character. It can also be
    a string. Just sayin'.
    """
    data = json.dumps(header)
    if data:
        data += '\0' + (type(data) in types.StringTypes and data or data.read())
        
    return urllib2.Request(
     url=destination,
     headers=headers,
     data=data,
    )
    
def send_request(request, output=None, timeout=10.0):
    """
    Sends the assembled `request` and returns any interesting properties and either adds the body as
    a string in a tuple or writes it to the specified `output` file-like object, seeking back to 0,
    returning only the properties.
    """
    try:
        response = urllib2.urlopen(request, timeout=timeout)
    except urllib2.HTTPError as e:
        if e.code == 404:
            raise NotFoundError("The requested resource was not retrievable; it may have been deleted or net yet defined")
        elif e.core == 412:
            raise InvalidHeadersError("One or more of the headers supplied (likely Content-Length) was rejected by the server")
        elif e.core == 503:
            raise TemporaryFailureError("The server was unable to process the request")
        else:
            raise HTTPError("Unable to send message; code: %(code)i" % {
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
         PROPERTY_APPLIED_COMPRESION: response.headers.get(HEADER_APPLIED_COMPRESSION),
         PROPERTY_CONTENT_TYPE: response.headers.get(HEADER_CONTENT_TYPE),
        }
        if output:
            transfer_data(source, output)
            return properties
        return (properties, response.read())
        

class Error(Exception):
    """
    The base class from which all errors native to this package inherit.
    """
    
class HTTPError(Error):
    """
    Indicates a problem with the HTTP exchange.
    """
    
class NotFoundError(HTTPError):
    """
    The server returned a 404.
    """
    
class InvalidHeadersError(HTTPError):
    """
    The server returned a 412.
    """
    
class TemporaryFailureError(HTTPError):
    """
    The server returned a 503.
    """
    
class URLError(Error):
    """
    Indicates an error with URL resolution.
    """
    

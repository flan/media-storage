"""
Shared functions and stuff. Mostly just HTTP access methods.
"""
import hashlib
import json
import types
import urllib2

#Request headers
HEADER_COMPRESS_ON_SERVER = 'Media-Storage-Compress-On-Server'
HEADER_COMPRESS_ON_SERVER__TRUE = 'yes'
HEADER_COMPRESS_ON_SERVER__FALSE = 'no' #Implied by omission
HEADER_SUPPORTED_COMPRESSION = 'Media-Storage-Supported-Compression'
HEADER_SUPPORTED_COMPRESSION_DELIMITER = ';'
#Response headers
HEADER_APPLIED_COMPRESSION = 'Media-Storage-Applied-Compression'
HEADER_CONTENT_TYPE = 'Content-Type'
#Response properties
PROPERTY_CONTENT_TYPE = 'content-type'
PROPERTY_APPLIED_COMPRESSION = 'applied-compression'

_CHUNK_SIZE = 32 * 1024 #Transfer data in 32k chunks

def process_file(file):
    """
    Returns the file's content as a string, computing its sha256 checksum along the way; both values
    are returned in a tuple.
    """
    global _CHUNK_SIZE
    buffer = []
    hash = hashlib.sha256()
    while True:
        chunk = file.read(_CHUNK_SIZE)
        if chunk:
            hash.update(chunk)
            buffer.append(chunk)
        else:
            break
    return (''.join(buffer), hash.hexdigest())
    
def assemble_request(destination, header, file=None, headers={}):
    """
    `destination` is the URI to which the request will be sent.
    
    `headers` is a dictionary containing any optional headers to be sent to the server, in addition
    to any required by the protocol (new headers will overwrite base ones).

    `header` is the JSON structure that contains the semantics of the request.
    
    `file`, if present, is a file-like object with additional binary content to be attached to the
    request, used only for uploading. It is appended after the JSON header, delimited by a null
    character.
    """
    data = json.dumps(header)
    if file:
        data += '\0' + file
        
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
    except Exception as e:
        #TODO: Add exceptions for cases from which recovery is possible, like 404, 408, and 503
        raise
    else:
        properties = {
         PROPERTY_APPLIED_COMPRESION: response.headers.get(HEADER_APPLIED_COMPRESSION),
         PROPERTY_CONTENT_TYPE: response.headers.get(HEADER_CONTENT_TYPE),
        }
        if output:
            while True:
                chunk = response.read(_CHUNK_SIZE)
                if not chunk:
                    break
                output.write(chunk)
                output.flush()
            output.seek(0)
            return properties
        return (properties, response.read())
        

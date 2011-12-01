"""
Shared functions and stuff. Mostly just HTTP access methods.
"""
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

def _process_data(data):
    if not type(data) in types.StringTypes:
        if type(data) is dict:
            return json.dumps(data)
        else:
            return data.read()
        raise ValueError("Unexpected data-type received: %(data)r" % {
         'data': data,
        })
    return data
    
def assemble_request(destination, headers={}, data=None):
    """
    `destination` is the URI to which the request will be sent.
    
    `headers` is a dictionary containing any optional headers to be sent to the server, in addition
    to any required by the protocol (new headers will overwrite base ones).
    
    `data` may, if not None, either be a string-type, a dictionary, or a file-like object, with
    file-like objects being read and passed as strings and dictionaries being converted to JSON,
    then passed as strings. If `data` is a sequence, each element will be individually processed
    and separated by a null character in the bytestream.
    """
    if data:
        if type(data) in (list, tuple):
            data = '\0'.join((_process_data(d) for d in data))
        else:
            data = _process_data(data)
            
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
        #TODO: Add exceptions for cases from which recovery is possible, like 404 and 503
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
        

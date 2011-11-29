"""
Provides an array of backend implementations.
"""
import logging
import re

from common import (
 Error,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
from local import LocalBackend
from sftp import SFTPBackend

_URI_RE = re.compile(
 r'(?P<schema>[a-z]+)://(?:(?P<username>.+?)(?::(?P<password>.+?))?@)?(?P<host>.*?)(?::(?P<port>\d+))?(?P<path>/.*)'
) #Matches 'http://whee.whoo:desu@uguu.ca:82/cheese'

_logger = logging.getLogger("media_storage.backends")

def get_backend(uri):
    """
    Given a `uri` of the form '<schema>://[<username>[:<password>]@]<host>[:port]<path>',
    constructs and returns the appropriate backend.
    
    Raises UnknownSchemaError if unable to work with the given URI.
    """
    match = _URI_RE.match(uri)
    if not match:
        _logger.error("Unable to parse URI")
        raise UnknownSchemaError(uri)
        
    (schema, username, password, host, port, path) = match.groups()
    if port:
        port = int(port)
    _logger.info("Building backend instance for %(path)s%(host)s via the %(schema)s protocol..." % {
     'path': path,
     'host': '%(host)s%(port)s' % {
      'host': host and '@' + host or '',
      'port': port and ':' + port or '',
     },
     'schema': schema,
    })
    
    if schema == 'file':
        return LocalBackend(path)
    elif schema == 'sftp':
        return SFTPBackend(username, password, host, port, path)
        
    _logger.error("Unknown schema")
    raise UnknownSchemaError("'%(schema)s' does not match any recognised type" % {
     'schema': schema,
    })
    
class UnknownSchemaError(Exception):
    """
    The given URI does not identify any supported backend.
    """
    

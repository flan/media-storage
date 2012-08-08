"""
media-storage_server.backends
=============================

Provides an array of backend implementations to support diverse filesystem types with a common
interface.

This module itself specifically provides a factory method, `get_backend()`, that makes the
abstraction seamless. In addition to that, it exposes key classes, like exceptions, from the rest of
the package, precluding the need for developers to dig through the code or maintain lengthy
references.

Legal
+++++
 This file is part of media-storage.
 media-storage is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 
 (C) Neil Tallim, 2012 <flan@uguu.ca>
"""
import logging
import re

from common import (
 Error,
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
from local import LocalBackend

_URI_RE = re.compile(
 r'(?P<schema>[a-z]+)://(?:(?P<username>.+?)(?::(?P<password>.+?))?@)?(?P<host>.*?)(?::(?P<port>\d+))?(?P<path>/.*)'
) #Matches 'http://whee.whoo:desu@uguu.ca:82/cheese'

_logger = logging.getLogger("media_storage.backends")

def get_backend(uri):
    """
    Given a `uri` of the form '<schema>://[<username>[:<password>]@]<host>[:port]<path>',
    constructs and returns the appropriate backend, an instance of ``common.BaseBackend``.
    
    Raises ``UnknownSchemaError`` if unable to work with the given URI.
    """
    tokens = uri.split(':')
    options = tokens[:-2]
    uri = tokens[-2] + ':' + tokens[-1]
    match = _URI_RE.match(uri)
    if not match:
        _logger.error("Unable to parse URI")
        raise UnknownSchemaError(uri)
        
    (schema, username, password, host, port, path) = match.groups()
    if port:
        port = int(port)
    _logger.info("Building backend instance for %(path)s%(host)s via the %(schema)s protocol with options %(options)s..." % {
     'path': path,
     'host': '%(host)s%(port)s' % {
      'host': host and '@' + host or '',
      'port': port and ':' + port or '',
     },
     'schema': schema,
     'options': options or '<none>',
    })
    
    if schema == 'file':
        return LocalBackend(path, options)
        
    _logger.error("Unknown schema")
    raise UnknownSchemaError("'%(schema)s' does not match any recognised type" % {
     'schema': schema,
    })
    
class UnknownSchemaError(Exception):
    """
    The given URI does not identify any supported backend.
    """
    

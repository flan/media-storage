"""
media-storage_server.state
==========================

Retains all important runtime state for the server in a central location.

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

_FAMILIES = {}

_logger = logging.getLogger('media_storage.state')

def register_family(family, filesystem):
    """
    `family` is the name of the family to be registered and `filesystem` is the backend instance
    with which it is associated.
    
    A ``None`` family must be registered, which is used to resolve generic references.
    """
    _logger.info("Registered %(family)s family" % {
     'family': (family and "'" + family + "'") or 'generic',
    })
    _FAMILIES[family] = filesystem
    
def get_filesystem(family):
    """
    Retrieves the filesystem instance associated with the specified `family`, or the generic
    filesystem if the family is None or undefined.
    """
    filesystem = _FAMILIES.get(family)
    if filesystem:
        _logger.debug("Retrieved filesystem reference for '%(family)s' family" % {
         'family': family,
        })
    else:
        filesystem = _FAMILIES.get(None)
        _logger.debug("Retrieved filesystem reference for generic family")
    return filesystem
    
def get_families():
    """
    Enumerates all families registered in the system, including the mandatory ``None``.
    """
    return _FAMILIES.keys()
    

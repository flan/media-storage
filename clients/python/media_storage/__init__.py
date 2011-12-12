"""
media_storage
=============

media_storage is a package that exposes classes and constants needed to
interact with services in a media-storage envronment.

Usage
-----

Importing this package and using only the objects it directly exposes is the
recommended way to use media_storage.
 
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
from common import (
 QueryStruct,
 Error,
 HTTPError, NotAuthorisedError, NotFoundError, InvalidRecordError, InvalidHeadersError,
 TemporaryFailureError,
 URLError,
)

from compression import (
 COMPRESS_NONE, COMPRESS_BZ2, COMPRESS_GZ, COMPRESS_LZMA,
)
COMPRESSION_FORMATS = (COMPRESS_NONE, COMPRESS_BZ2, COMPRESS_GZ, COMPRESS_LZMA,)

from client import Client
from storage_proxy import StorageProxyClient
from caching_proxy import CachingProxyClient


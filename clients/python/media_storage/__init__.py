"""
Exposes implemented classes as the front-end for the library.
"""
from common import (
 Error,
 HTTPError, NotFoundError, InvalidRecordError, InvalidHeadersError, TemporaryFailureError,
 URLError,
)

from compression import (
 COMPRESS_NONE, COMPRESS_BZ2, COMPRESS_GZ, COMPRESS_LZMA,
)
COMPRESSION_FORMATS = (COMPRESS_NONE, COMPRESS_BZ2, COMPRESS_GZ, COMPRESS_LZMA,)

from interfaces import QueryStruct
from client import Client
from storage_proxy import StorageProxyClient
from caching_proxy import CachingProxyClient


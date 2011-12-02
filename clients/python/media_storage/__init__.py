"""
Exposes implemented classes as the front-end for the library.
"""
from compression import (
 COMPRESS_NONE, COMPRESS_BZ2, COMPRESS_GZIP, COMPRESS_LZMA,
)

from interfaces import QueryStruct
from client import Client
from storage_proxy import StorageProxyClient
from caching_proxy import CachingProxyClient


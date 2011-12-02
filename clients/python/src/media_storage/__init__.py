"""
Exposes implemented classes as the front-end for the library.
"""
from compression import (
 COMPRESS_NONE, COMPRESS_BZ2, COMPRESS_GZIP, COMPRESS_LZMA,
)

from server import Client
from proxy import ProxyClient
from caching_proxy import CachingProxyClient


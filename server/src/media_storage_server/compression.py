"""
media-storage : compression
===========================

Offers efficient handlers for compressing and decompressing data, using
file-like objects (often tempfiles).

This module is shared by every Python facet of the media-storage project and
changes to one instance should be reflected in all.

Usage
-----

(De)compressors may be called explicitly or retrieved with one of the getter
functions.
 
Legal
-----

This file is part of the LGPLed subset of the media-storage project.
This module is free software; you can redistribute it and/or modify
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
import bz2
import logging
import tempfile
import zlib

try:
    import lzma
except ImportError:
    lzma = None
    
#Compression type constants
COMPRESS_NONE = None
COMPRESS_BZ2 = 'bz2'
COMPRESS_GZIP = 'gzip'
COMPRESS_LZMA = 'lzma'

SUPPORTED_FORMATS = [COMPRESS_GZIP, COMPRESS_BZ2]
if lzma:
    SUPPORTED_FORMATS.append(COMPRESS_LZMA)
SUPPORTED_FORMATS = tuple(SUPPORTED_FORMATS)

_MAX_SPOOLED_FILESIZE = 1024 * 256 #Allow up to 256k in memory
_BUFFER_SIZE = 1024 * 32 #Work with 32k chunks

_logger = logging.getLogger('media_server-compression')

def get_compressor(format):
    """
    Returns a callable that accepts a file-like object and returns a compressed version of the
    file's contents as a file-like object.
    
    `format` is the format to which conversion should occur, one of the compression type constants.
    """
    if format is COMPRESS_NONE:
        return (lambda x:x)
    elif format == COMPRESS_GZIP:
        return compress_gzip
    elif format == COMPRESS_BZ2:
        return compress_bz2
    elif format == COMPRESS_LZMA and lzma:
        return compress_lzma
    raise ValueError(format + " is unsupported")
    
def get_decompressor(format):
    """
    Returns a callable that accepts a file-like object and returns a decompressed version of the
    file's contents as a file-like object.
    
    `format` is the format from which conversion should occur, one of the compression type constants.
    """
    if format is COMPRESS_NONE:
        return (lambda x:x)
    elif format == COMPRESS_GZIP:
        return decompress_gzip
    elif format == COMPRESS_BZ2:
        return decompress_bz2
    elif format == COMPRESS_LZMA and lzma:
        return decompress_lzma
    raise ValueError(format + " is unsupported")
    
def _process(data, handler, flush_handler):
    """
    Iterates over the given `data`, reading a reasonable number of bytes, passing them through the
    given (de)compression `handler`, and writing the output to a temporary file, which is ultimately
    returned (seeked to 0).
    
    If an exception occurs, it is raised directly.
    """
    try:
        temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
        while True:
            chunk = data.read(_BUFFER_SIZE)
            if chunk:
                chunk = handler(chunk)
                if chunk:
                    temp.write(chunk)
            else:
                if flush_handler:
                    chunk = flush_handler()
                    if chunk:
                        temp.write()
                break
        temp.flush()
        temp.seek(0)
        return temp
    except Exception as e:
        _logger.error("A problem occurred during (de)compression: %(error)s" % {
         'error': str(e),
        })
        raise
        
def compress_bz2(data):
    """
    Compresses the given file-like object `data` with the bz2 algorithm, returning a file-like
    object and its size in a tuple.
    
    Any exceptions are raised directly.
    """
    _logger.debug("Compressing data with bz2...")
    compressor = bz2.BZ2Compressor()
    return _process(data, compressor.compress, compressor.flush)

def decompress_bz2(data):
    """
    Decompresses the given file-like object `data` with the bz2 algorithm, returning a file-like
    object and its size in a tuple.
    
    Any exceptions are raised directly.
    """
    _logger.debug("Decompressing data with bz2...")
    decompressor = bz2.BZ2Decompressor()
    return _process(data, decompressor.decompress, None)
    
def compress_gzip(data):
    """
    Compresses the given file-like object `data` with the gzip algorithm, returning a file-like
    object and its size in a tuple.
    
    Any exceptions are raised directly.
    """
    _logger.debug("Compressing data with gzip...")
    compressor = zlib.compressobj()
    return _process(data, compressor.compress, compressor.flush)
    
def decompress_gzip(data):
    """
    Decompresses the given file-like object `data` with the gzip algorithm, returning a file-like
    object and its size in a tuple.
    
    Any exceptions are raised directly.
    """
    _logger.debug("Decompressing data with gzip...")
    decompressor = zlib.decompressobj()
    return _process(data, decompressor.decompress, decompressor.flush)
    
if lzma: #If the module is unavailable, don't even define the functions
    def compress_lzma(data):
        """
        Compresses the given file-like object `data` with the lzma algorithm, returning a file-like
        object and its size in a tuple.
        
        Any exceptions are raised directly.
        
        This function is not available if no LZMA library is present.
        """
        _logger.debug("Compressing data with lzma...")
        compressor = lzma.LZMACompressor()
        return _process(data, compressor.compress, compressor.flush)
        
    def decompress_lzma(data):
        """
        Decompresses the given file-like object `data` with the lzma algorithm, returning a
        file-like object and its size in a tuple.
        
        Any exceptions are raised directly.
        
        This function is not available if no LZMA library is present.
        """
        _logger.debug("Decompressing data with lzma...")
        decompressor = lzma.LZMADecompressor()
        return _process(data, decompressor.decompress, decompressor.flush)
        

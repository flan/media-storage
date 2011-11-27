"""
Offers efficient handlers for compressing and decompressing data, working with
file-like objects (often tempfiles).
#Names are reflectable
"""
import bz2
import logging
import tempfile
import zlib

import lzma

SUPPORTED_FORMATS = ('gzip', 'bz2', 'lzma',)

_MAX_SPOOLED_FILESIZE = 1024 * 256 #Allow up to 256k in memory
_BUFFER_SIZE = 1024 * 32 #Work with 32k chunks

_logger = logging.getLogger('media_server.compression')

def _process(data, handler, flush_handler):
    """
    Iterates over the given `data`, reading a reasonable number of bytes, passing them through the
    given (de)compression `handler`, and writing the output to a temporary file, which is ultimately
    returned.
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
                    temp.write(flush_handler())
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
    compressor = bz2.BZ2Compressor()
    return _process(data, compressor.compress, compressor.flush)

def decompress_bz2(data):
    decompressor = bz2.BZ2Decompressor()
    return _process(data, decompressor.decompress, None)
    
def compress_gzip(data):
    compressor = zlib.compressobj()
    return _process(data, compressor.compress, compressor.flush)
    
def decompress_gzip(data):
    decompressor = zlib.decompressobj()
    return _process(data, decompressor.decompress, decompressor.flush)
    
def compress_lzma(data):
    compressor = lzma.LZMACompressor()
    return _process(data, compressor.compress, compressor.flush)
    
def decompress_lzma(data):
    decompressor = lzma.LZMADecompressor()
    return _process(data, decompressor.decompress, decompressor.flush)
    

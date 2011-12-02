"""
Offers efficient handlers for compressing and decompressing data, working with
file-like objects (often tempfiles).
#Names are reflectable
"""
import bz2
import logging
import tempfile
import zlib

try:
    import lzma
except ImportError:
    lzma = None
    
SUPPORTED_FORMATS = ['gzip', 'bz2']
if lzma:
    SUPPORTED_FORMATS.append('lzma')
SUPPORTED_FORMATS = tuple(SUPPORTED_FORMATS)

#Compression types
COMPRESS_NONE = None
COMPRESS_BZ2 = 'bz2'
COMPRESS_GZIP = 'gzip'
COMPRESS_LZMA = 'lzma'

_MAX_SPOOLED_FILESIZE = 1024 * 256 #Allow up to 256k in memory
_BUFFER_SIZE = 1024 * 32 #Work with 32k chunks

_logger = logging.getLogger('media_server.compression')

def get_compressor(format):
    if format == 'gzip':
        return compress_gzip
    elif format == 'bz2':
        return compress_bz2
    elif format == 'lzma' and lzma:
        return compress_lzma
    raise ValueError(format + " is unsupported")
    
def get_decompressor(format):
    if format == 'gzip':
        return decompress_gzip
    elif format == 'bz2':
        return decompress_bz2
    elif format == 'lzma' and lzma:
        return decompress_lzma
    raise ValueError(format + " is unsupported")
    
def _process(data, handler, flush_handler):
    """
    Iterates over the given `data`, reading a reasonable number of bytes, passing them through the
    given (de)compression `handler`, and writing the output to a temporary file, which is ultimately
    returned (seeked to 0), along with its size, in a tuple.
    """
    size = 0
    try:
        temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
        while True:
            chunk = data.read(_BUFFER_SIZE)
            if chunk:
                chunk = handler(chunk)
                if chunk:
                    size += len(chunk)
                    temp.write(chunk)
            else:
                if flush_handler:
                    chunk = flush_handler()
                    if chunk:
                        size += len(chunk)
                        temp.write()
                break
        temp.flush()
        temp.seek(0)
        return (temp, size)
    except Exception as e:
        _logger.error("A problem occurred during (de)compression: %(error)s" % {
         'error': str(e),
        })
        raise
        
def compress_bz2(data):
    _logger.debug("Compressing data with bz2...")
    compressor = bz2.BZ2Compressor()
    return _process(data, compressor.compress, compressor.flush)

def decompress_bz2(data):
    _logger.debug("Decompressing data with bz2...")
    decompressor = bz2.BZ2Decompressor()
    return _process(data, decompressor.decompress, None)
    
def compress_gzip(data):
    _logger.debug("Compressing data with gzip...")
    compressor = zlib.compressobj()
    return _process(data, compressor.compress, compressor.flush)
    
def decompress_gzip(data):
    _logger.debug("Decompressing data with gzip...")
    decompressor = zlib.decompressobj()
    return _process(data, decompressor.decompress, decompressor.flush)
    
def compress_lzma(data):
    _logger.debug("Compressing data with lzma...")
    compressor = lzma.LZMACompressor()
    return _process(data, compressor.compress, compressor.flush)
    
def decompress_lzma(data):
    _logger.debug("Decompressing data with lzma...")
    decompressor = lzma.LZMADecompressor()
    return _process(data, decompressor.decompress, decompressor.flush)
    
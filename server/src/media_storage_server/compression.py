"""
Offers efficient handlers for compressing and decompressing data, working with
file-like objects (often tempfiles).
"""
import bz2
import tempfile
import zlib

import lzma

_MAX_SPOOLED_FILESIZE = 1024 * 128 #Allow up to 128k in memory
_BUFFER_SIZE = 1024 * 16 #Work with 16k chunks

#Names are reflectable

def _process(data, handler, flush_handler):
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
    

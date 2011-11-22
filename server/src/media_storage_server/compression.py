"""
Offers efficient handlers for compressing and decompressing data, working with
file-like objects (often tempfiles).
"""
import bz2
import tempfile
import zlib

import lzma

_MAX_SPOOLED_FILESIZE = 1024 * 128 #Allow up to 128k in memory
_BUFFER_SIZE = 1024 * 32 #Work with 32k chunks

#Names are reflectable

def compress_bz2(data):
    compressor = bz2.BZ2Compressor()
    temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
    while True:
        chunk = data.read(_BUFFER_SIZE)
        if chunk:
            chunk = compressor.compress(chunk)
            if chunk:
                temp.write(chunk)
        else:
            temp.write(compressor.flush())
            break
    temp.flush()
    temp.seek(0)
    return temp

def decompress_bz2(data):
    decompressor = bz2.BZ2Decompressor()
    temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
    while True:
        chunk = data.read(_BUFFER_SIZE)
        if chunk:
            chunk = decompressor.decompress(chunk)
            if chunk:
                temp.write(chunk)
        else:
            break
    temp.flush()
    temp.seek(0)
    return temp
    
def compress_gzip(data):
    compressor = zlib.compressobj()
    temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
    while True:
        chunk = data.read(_BUFFER_SIZE)
        if chunk:
            chunk = compressor.compress(chunk)
            if chunk:
                temp.write(chunk)
        else:
            temp.write(compressor.flush())
            break
    temp.flush()
    temp.seek(0)
    return temp

def decompress_gzip(data):
    decompressor = zlib.decompressobj()
    temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
    while True:
        chunk = data.read(_BUFFER_SIZE)
        if chunk:
            chunk = decompressor.decompress(chunk)
            if chunk:
                temp.write(chunk)
        else:
            temp.write(decompressor.flush())
            break
    temp.flush()
    temp.seek(0)
    return temp
    
def compress_lzma(data):
    compressor = lzma.LZMACompressor()
    temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
    while True:
        chunk = data.read(_BUFFER_SIZE)
        if chunk:
            chunk = compressor.compress(chunk)
            if chunk:
                temp.write(chunk)
        else:
            temp.write(compressor.flush())
            break
    temp.flush()
    temp.seek(0)
    return temp
    
def decompress_lzma(data):
    decompressor = lzma.LZMADecompressor()
    temp = tempfile.SpooledTemporaryFile(_MAX_SPOOLED_FILESIZE)
    while True:
        chunk = data.read(_BUFFER_SIZE)
        if chunk:
            chunk = decompressor.decompress(chunk)
            if chunk:
                temp.write(chunk)
        else:
            temp.write(decompressor.flush())
            break
    temp.flush()
    temp.seek(0)
    return temp
    

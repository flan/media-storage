"""
Offers efficient handlers for compressing and decompressing data, working with
file-like objects (often tempfiles).
"""
import bz2
import gzip

FORMATS = ['bz2', 'gzip']

try:
    import lzma
except Exception as e:
    _log.write('Unable to add support for LZMA: ' + str(e))
    lzma = None
else:
    FORMATS.append('lzma')
    
FORMATS = tuple(FORMATS)



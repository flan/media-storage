import logging

_FAMILIES = {}

_logger = logging.getLogger('media_storage.state')

def register_family(family, filesystem):
    """
    A None family must be registered, which is used to resolve generic references.
    """
    _logger.info("Registered %(family)s family" % {
     'family': (family and "'" + family + "'") or 'generic',
    })
    _FAMILIES[family] = filesystem
    
def get_filesystem(family):
    filesystem = _FAMILIES.get(family)
    if filesystem:
        _logger.debug("Retrieved filesystem reference for '%(family)s' family" % {
         'family': family,
        })
    else:
        filesystem = _FAMILIES.get(None)
        _logger.debug("Retrieved filesystem reference for generic family")
    return filesystem
    
def get_families():
    return _FAMILIES.keys()
    

_FAMILIES = {}

def _register_family(family, filesystem):
    """
    A None family must be registered, which is used to resolve generic references.
    """
    _FAMILIES[family] = filesystem
    
def get_filesystem(family)
    return _FAMILIES.get(family) or _FAMILIES.get(None)
    
def get_families():
    return _FAMILIES.keys()
    

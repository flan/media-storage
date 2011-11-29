from common import (
 FileNotFoundError, PermissionsError, CollisionError, NotEmptyError, NoSpaceError,
 NoFilehandleError,
)
import directory

class SFTPBackend(directory.DirectoryBackend):
    pass
    
    #_walk() will need to be a generator function defined internally
    

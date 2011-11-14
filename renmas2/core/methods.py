
from .structures import Structures

_structs = Structures()

def get_structs(names):
    return _structs.structs(names)


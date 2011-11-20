
from .structures import Structures

_structs = Structures()

def get_structs(names):
    return _structs.structs(names)

def compiled_struct(name):
    return _structs.get_compiled_struct(name)


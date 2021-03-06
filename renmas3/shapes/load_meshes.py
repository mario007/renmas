
import os.path

from .obj import Obj
from .ply import Ply

def load_obj(fname, material_loader=None):
    if not os.path.isfile(fname):
        return None #file doesn't exists
    obj = Obj()
    return obj.load(fname, material_loader)

def load_ply(fname):
    if not os.path.isfile(fname):
        return None #file doesn't exists
    ply = Ply()
    return ply.load(fname)

def load_meshes(fname, material_loader=None):
    if not os.path.isfile(fname):
        return None #file doesn't exists

    name, ext = os.path.splitext(fname)
    if ext == "": 
        return None
    ext = ext[1:] #Remove period from extension
    if ext == "obj":
        return load_obj(fname, material_loader)
    elif ext == "ply":
        return load_ply(fname)
    else:
        return None


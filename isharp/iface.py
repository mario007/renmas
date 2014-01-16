
from .utils import create_image, convert_to_bgra, load_hdr_image
from .itmo import create_tmo

#This will hold objects created from Charp
_objects = {}

def free_obj(id_obj):
    if id_obj in _objects:
        del _objects[id_obj]
        return 1
    return -1

_functions = {}
_functions['create_image'] = create_image
_functions['convert_to_bgra'] = convert_to_bgra
_functions['load_hdr_image'] = load_hdr_image
_functions['create_tmo'] = create_tmo

def exec_func(name, args):
    """Functions through wich we call other python functions.
       Functions that are call accept arguments as one
       string that they must parse and also they must
       return string.
    """
    func = _functions[name]
    return func(_objects, args)


def exec_method(id_obj, name, args):
    """Functions through wich we call other python methods.
       Functions that are call accept arguments as one
       string that they must parse and also they must
       return  string.
    """
    if id_obj not in _objects:
        raise ValueError("Object doesn't exist in objects!")
    obj = _objects[id_obj]
    method = getattr(obj, name)
    return method(_objects, args)


def _obj_to_string(obj, typ):
    if typ == 'float':
        return str(obj)
    elif typ == 'int':
        return str(obj)
    else:
        raise ValueError("Not suported %s type" % typ)


def get_prop(id_obj, name, typ):
    if id_obj in _objects:
        obj = _objects[id_obj]
        prop = getattr(obj, name)
        return _obj_to_string(prop, typ)
    else:
        raise ValueError("Object %s doesn't exist" % id_obj)

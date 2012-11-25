
from ..base import ImagePRGBA, ImageRGBA, ImageBGRA
from ..utils import blt_rgba, blt_prgba_to_bgra

_objects = {}

def create_image(args):
    pix_format, width, height = args.split(',')
    if pix_format == 'RGBA':
        img = ImageRGBA(int(width), int(height))
    elif pix_format == 'BGRA':
        img = ImageBGRA(int(width), int(height))
    elif pix_format == 'PRGBA':
        img = ImagePRGBA(int(width), int(height))
    else:
        raise ValueError("Unknown pixel format", pix_format)

    _objects[str(id(img))] = img
    return str(id(img))

def conv_to_bgra(args):
    id_obj = args
    if id_obj not in _objects:
        raise ValueError("Image doesn't exist in objects!")
    img = _objects[id_obj]
    width, height = img.size()
    if isinstance(img, ImageRGBA):
        new_img = img.to_bgra()
    elif isinstance(img, ImageBGRA):
        new_img = ImageBGRA(width, height)
        blt_rgba(img, new_img)
    elif isinstance(img, ImagePRGBA):
        new_img = ImageBGRA(width, height)
        blt_prgba_to_bgra(img, new_img)

    _objects[str(id(new_img))] = new_img
    return str(id(new_img))

def exec_method(id_obj, name, args):
    pass

#func must return string
def exec_func(name, args):
    if name in globals():
        func = globals()[name]
        return func(args)
    else:
        return str(None)

def _obj_to_string(obj, typ):
    if typ == 'float':
        return str(obj)
    elif typ == 'int':
        return str(obj)
    else:
        raise ValueError("Not suported type")

def _string_to_obj(text, typ):
    if typ == 'float':
        return float(text)
    elif typ == 'int':
        return int(text)
    else:
        raise ValueError("Not suported type")

def get_prop(id_obj, name, typ):
    if id_obj in _objects:
        obj = _objects[id_obj]
        prop = getattr(obj, name)
        return _obj_to_string(prop, typ)
    else:
        raise ValueError("Object %s doesn't exist" % id_obj)

def free_obj(id_obj):
    if id_obj in _objects:
        del _objects[id_obj]
        return 1
    return -1


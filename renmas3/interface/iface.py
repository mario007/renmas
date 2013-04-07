
from ..base import ImagePRGBA, ImageRGBA, ImageBGRA
from ..utils import blt_rgba, blt_prgba_to_bgra
from ..renderer import Renderer

_objects = {}

class IRenderer:
    def __init__(self, ren):
        self.ren = ren

    def parse_scene_file(self, args):
        fname = args
        self.ren.parse_scene_file(fname)
        return ''

    def open_project(self, args):
        fname = args
        self.ren.open_project(fname)
        return ''

    def save_project(self, args):
        fname = args
        self.ren.save_project(fname)
        return ''

    def render(self, args):
        ret = self.ren.render()
        return str(ret)

    def output_image(self, args):
        img = self.ren.output_image()
        width, height = img.size()
        ptr, pitch = img.address_info()
        ret = "%s,%s,%s,%s" % (str(width), str(height), str(ptr), str(pitch))
        return ret

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

def create_renderer(args):
    ren = Renderer()
    iren = IRenderer(ren)
    _objects[str(id(iren))] = iren
    return str(id(iren))

#NOTE func must return string
def exec_method(id_obj, name, args):
    if id_obj not in _objects:
        raise ValueError("Object doesn't exist in objects!")
    obj = _objects[id_obj]
    method = getattr(obj, name)
    return method(args)

_functions = {}
_functions['conv_to_bgra'] = conv_to_bgra
_functions['create_image'] = create_image
_functions['create_renderer'] = create_renderer

#NOTE func must return string
def exec_func(name, args):
    func = _functions[name]
    return func(args)

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


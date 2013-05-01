import inspect
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

    def get_prop(self, args):
        """ Protocol: type_name, name, group
            type_name - options, tone, sampler, camera, material, light, undefined  
            name - name of the property
            group - it is intended to use as light name, material name, etc....
            return - value of property as string
        """
        words = args.split(',')
        if words[0] == 'options':
            return self._get_option(words[1])
        if words[0] == 'tone':
            prop = self.ren._project.tmo.get_prop(words[1])
            return self._get_prop_value(prop)
        else:
            raise ValueError("Not yet implemented get prop")
        return ''

    def set_prop(self, args):
        """ Protocol: type_name, name, group, value
            type_name - options, tone, sampler, camera, material, light, undefined  
            name - name of the property
            group - it is intended to use as light name, material name, etc....
            value - value of property as string separated by comma val1, val2, ...
        """
        words = args.split(',')
        value = words[3:]
        if words[0] == 'options':
            self._set_option(words[1], value)
        elif words[0] == 'tone':
            prop = self.ren._project.tmo.get_prop(words[1])
            val = self._convert_prop_value(prop, value)
            self.ren._project.tmo.set_prop(words[1], val)
        else:
            raise ValueError("Not yet implemented set prop")
        return ''

    def get_props_descs(self, args):
        words = args.split(',')
        if words[0] == 'options':
            return 'int,resx,int,resy'
        elif words[0] == 'tone':
            return self._get_props_descs(self.ren._project.tmo.get_props())
        else:
            raise ValueError("Not yet implemented get props descs")
        return ''

    def _get_option(self, name):
        if name == 'resx':
            width, height = self.ren._film._hdr_image.size()
            return str(width)
        elif name == 'resy':
            width, height = self.ren._film._hdr_image.size()
            return str(height)
        else:
            raise ValueError("Unsuported option ", name)

    def _set_option(self, name, value):
        """  
            value - value of property as string separated by comma val1, val2, ...
        """
        if name == 'resx':
            width, height = self.ren._film._hdr_image.size()
            self.ren._film.set_resolution(int(value[0]), height)
        elif name == 'resy':
            width, height = self.ren._film._hdr_image.size()
            self.ren._film.set_resolution(width, int(value[0]))
        else:
            raise ValueError("Unsuported option ", name)
        return ''

    def _get_props_descs(self, props):
        descs = []
        for key, value in props.items():
            if inspect.isclass(value):
                continue
            if isinstance(value, int):
                descs.append('int')
                descs.append(key)
            elif isinstance(value, float):
                descs.append('float')
                descs.append(key)
            else:
                raise ValueError("Not supported type of prop ", key, value)
        return ','.join(descs)

    def _get_prop_value(self, prop):
        if isinstance(prop, int):
            return str(prop)
        elif isinstance(prop, float):
            return str(prop)
        else:
            raise ValueError("Not yet implemented get prop value")
    
    def _convert_prop_value(self, prop, value):
        if isinstance(prop, int):
            return int(value[0])
        elif isinstance(prop, float):
            return float(value[0])
        else:
            raise ValueError("Not yet implemented convert prop value")


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


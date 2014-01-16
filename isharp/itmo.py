
from sdl.image import ImagePRGBA, ImageRGBA, ImageBGRA
from sdl.blt_floatrgba import blt_prgba_to_rgba
from sdl.args import FloatArg
from imldr import save_image
from hdr import Tmo


class ITmo:
    def __init__(self):
        self.tmapping = Tmo()
        self.tmapping.load('exp')

    def load(self, objects, args):
        shader_name = args
        self.tmapping.load(shader_name)
        return ""

    def tmo(self, objects, args):
        in_id, out_id = args.split(',')
        in_img = objects[in_id]
        out_img = objects[out_id]
        self.tmapping.tmo(in_img, out_img)
        return ""

    def get_prop(self, objects, args):
        key = args
        if key == 'q':
            return str(self.tmapping.shader.get_value('q'))
        elif key == 'k':
            return str(self.tmapping.shader.get_value('k'))
        elif key == 'gamma':
            return str(self.tmapping.shader.get_value('gamma'))
        raise ValueError("Wrong key %s" % key)

    def set_prop(self, objects, args):
        key, val = args.split(',')
        if key == 'q':
            self.tmapping.shader.set_value('q', float(val))
        elif key == 'k':
            self.tmapping.shader.set_value('k', float(val))
        elif key == 'gamma':
            self.tmapping.shader.set_value('gamma', float(val))
        else:
            raise ValueError("Wrong key %s" % key)
        return ""

    def get_public_props(self, objects, args):
        public_props = ''
        for a in self.tmapping.shader._args:
            if isinstance(a, FloatArg):
                public_props += ',' + a.name + ',' + 'float'
        if public_props == '':
            return ''
        return public_props[1:]

    def save_image(self, objects, args):
        fname, id_img = args.split(',')
        image = objects[id_img]
        if isinstance(image, ImagePRGBA):
            width, height = image.size()
            new_img = ImageRGBA(width, height)
            blt_prgba_to_rgba(image, new_img)
            save_image(fname, new_img)
        elif isinstance(image, ImageRGBA):
            save_image(fname, image)
        elif isinstance(image, ImageBGRA):
            new_img = image.to_rgba()
            save_image(fname, new_img)
        return ""


def create_tmo(objects, args):
    tmo = ITmo()
    objects[str(id(tmo))] = tmo 
    return str(id(tmo))


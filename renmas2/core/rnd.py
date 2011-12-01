
import renmas2.shapes
from renmas2.core import Vector3

def generate_name(self, obj):
    pass

class IRender:
    def __init__(self, renderer):
        self.renderer = renderer
    
    def create_shape(self, **kw):
        t = kw.get("type", None)
        if t is None: return #log!!! TODO
        if t == "sphere": self._create_sphere(kw)

    def _create_sphere(self, kw):
        radius = kw.get("radius", None)
        position = kw.get("position", None)
        name = kw.get("name", None)
        if radius is None or position is None or name is None: return #LOG TODO
        x, y, z = position
        sph = renmas2.shapes.Sphere(Vector3(float(x), float(y), float(z)), float(radius), None)
        self.renderer.add(name, sph)

    def options(self, **kw):
        asm = kw.get("asm", None)
        self.renderer.asm(bool(asm))

    def create_samplers(self, **kw):
        pass

    def create_camera(self, **kw):
        pass

    def set_props(self, category, name, value):
        if category == "camera":
            self._set_camera_props(name, value)
        elif category == "misc":
            self._set_misc(name, value)
        return 1

    def get_props(self, category, name):
        if category == "camera":
            return self._get_camera_props(name)
        elif category == 'misc':
            return self._get_misc(name)
        elif category == "frame_buffer":
            fb = self.renderer._film.frame_buffer
            w, h = fb.get_size()
            ptr, pitch = fb.get_addr()
            return str(w) + "," + str(h) + "," + str(pitch) + "," + str(ptr) 

        return ""

    def _set_camera_props(self, name, value):
        if name == "eye":
            x, y, z = value.split(',')
            self.renderer._camera.set_eye(x, y, z)
        elif name == "lookat":
            x, y, z = value.split(',')
            self.renderer._camera.set_lookat(x, y, z)
        elif name == "distance":
            self.renderer._camera.set_distance(value)

    def _get_camera_props(self, name):
        if name == "eye":
            x, y, z = self.renderer._camera.get_eye()
            return str(x) + "," + str(y) + "," + str(z) 
        elif name == "lookat":
            x, y, z = self.renderer._camera.get_lookat()
            return str(x) + "," + str(y) + "," + str(z) 
        elif name == "distance":
            return str(self.renderer._camera.get_distance())
        return ""

    def _set_misc(self, name, value):
        if name == "resolution":
            w, h = value.split(',')
            self.renderer.resolution(w, h)
        elif name == "spp":
            self.renderer.spp(value)
        elif name == "pixel_size":
            self.renderer.set_pixel_size(value)

    def _get_misc(self, name):
        if name == 'resolution':
            return str(self.renderer._width) + ',' + str(self.renderer._height)
        elif name == 'spp':
            return str(self.renderer._spp)
        elif name == 'pixel_size':
            return str(self.renderer._pixel_size)


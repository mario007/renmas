
from tdasm import Tdasm

from .vector3 import Vector3
from .ray import Ray
from ..lights import PointLight, DirectionalLight
from .shade_point import ShadePoint
from ..loaders import load_spd
from ..shapes import Sphere

class Factory:
    def __init__(self):
        pass

    def vector3(self, x, y, z):
        return Vector3(float(x), float(y), float(z))

    def ray(self, origin, direction, normalized=True):
        o = self.vector3(*origin)
        d = self.vector3(*direction)
        if normalized:
            d.normalize()
        return Ray(o, d)

    def sphere(self, origin, radius, material=None):
        o = self.vector3(*origin)
        radius = float(radius)
        return Sphere(o, radius, material)

    def create_shape(self, **kw):
        t = kw.get("type", None)
        if t is None:
            return None

        if t == "sphere": 
            radius = kw.get("radius", None)
            position = kw.get("position", None)
            if radius is None or position is None:
                return None
            return self.sphere(position, radius)
        return None

    def create_light(self, mgr=None, renderer=None, typ=None, position=None, \
            source=None, direction=None, scale=1.0, **kwargs):

        if mgr is None and renderer is None: 
            return None
        if mgr is None:
            mgr = renderer.color_mgr
        
        if source is None: 
            return None
        if isinstance(source, str):
            source = load_spd(source, 'light')
            if source is None:
                return None
        spec = mgr.create_spectrum(source)

        if typ == 'point': # create point light
            if position is None: 
                return None
            position = self.vector3(*position)
            return PointLight(position, spec, float(scale))
        elif typ == 'directional':
            if direction is None:
                return None
            direction = self.vector3(*direction)
            direction.normalize()
            return DirectionalLight(direction, spec, float(scale))

        return None

    def shade_point(self, t=0.0, hit=(1,1,1), normal=(0,1,0), material=None):

        hit = self.vector3(*hit)
        normal = self.vector3(*normal)
        
        return ShadePoint(t, hit, normal, material)



from tdasm import Tdasm
from ..materials import Lambertian
from ..lights import PointLight
from .spectrum import Spectrum
from .material import Material
from ..materials import Lambertian
from .vector3 import Vector3
from .ray import Ray
from ..shapes import Sphere, Triangle, Rectangle

from renmas2.macros import MacroCall, arithmetic32, arithmetic128,\
                            broadcast, macro_if, dot_product, normalization, cross_product

class Factory:
    def __init__(self):
        pass

    def create_assembler(self):
        assembler = Tdasm()
        macro_call = MacroCall()
        assembler.register_macro('call', macro_call.macro_call)
        assembler.register_macro('eq128', arithmetic128)
        assembler.register_macro('eq32', arithmetic32)
        assembler.register_macro('broadcast', broadcast)
        assembler.register_macro('if', macro_if)
        assembler.register_macro('dot', dot_product)
        assembler.register_macro('normalization', normalization)
        assembler.register_macro('cross', cross_product)
        return assembler

    def create_lambertian(self, spectrum, k=None):
        return Lambertian(spectrum, k)

    def vector(self, x, y, z):
        return Vector3(float(x), float(y), float(z))

    def create_ray(self, origin, direction):
        x, y, z = origin
        o = Vector3(float(x), float(y), float(z))
        x, y, z = direction
        d = Vector3(float(x), float(y), float(z))
        d.normalize()
        return Ray(o, d)

    def create_sphere(self, origin, radius, material=None):
        x, y, z = origin
        o = Vector3(float(x), float(y), float(z))
        radius = float(radius)
        return Sphere(o, radius, material)

    def create_triangle(self, v0, v1, v2, material=None, n0=None, n1=None, n2=None, u=None, v=None):
        x, y, z = v0 
        V0 = Vector3(float(x), float(y), float(z))
        x, y, z = v1 
        V1 = Vector3(float(x), float(y), float(z))
        x, y, z = v2 
        V2 = Vector3(float(x), float(y), float(z))
        N0 = N1 = N2 = U = V = None
        if n0 is not None:
            x, y, z = n0 
            N0 = Vector3(float(x), float(y), float(z))
        if n1 is not None:
            x, y, z = n1 
            N1 = Vector3(float(x), float(y), float(z))
        if n2 is not None:
            x, y, z = n2 
            N2 = Vector3(float(x), float(y), float(z))
        if u is not None:
            U = float(u)
        if v is not None:
            V = float(v)
        tr = Triangle(V0, V1, V2, material, N0, N1, N2, U, V)
        return tr

    def create_rectangle(self, point, e1, e2, normal, material=None):
        x, y, z = point 
        p = Vector3(float(x), float(y), float(z))
        x, y, z = e1 
        e1 = Vector3(float(x), float(y), float(z))
        x, y, z = e2 
        e2 = Vector3(float(x), float(y), float(z))
        x, y, z = normal 
        n = Vector3(float(x), float(y), float(z))
        r = Rectangle(p, e1, e2, n, material)
        return r

    def create_sampler(self, **kw):
        pass

    def create_camera(self, **kw):
        pass

    # linear intepolation 
    def lerp(self, t, v1, v2):
        return (1.0 - t) * v1 + t * v2


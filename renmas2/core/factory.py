
from ..materials import Lambertian
from ..lights import PointLight
from .spectrum import Spectrum
from .material import Material
from .vector3 import Vector3

class Factory:
    def __init__(self):
        pass

    def create_shape(self, **kw):
        pass

    def create_light(self, **kw):
        typ = kw.get("type")
        if typ == "point":
            p = kw.get("position")
            s = kw.get("spectrum")
            spec = Spectrum(float(s[0]), float(s[1]), float(s[2]))
            pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
            l = PointLight(pos, spec)
            return l


    def create_material(self, **kw): # TODO catch Exception and return None if exception ocur
        mat = Material()
        brdfs = kw.get("brdfs", None)
        if brdfs:
            for c in brdfs:
                lamb = c.get("lambertian", None)
                if lamb:
                    s = lamb.get("spectrum")
                    k = lamb.get("k", 1.0)
                    spec = Spectrum(float(s[0]), float(s[1]), float(s[2]))
                    l = Lambertian(spec, float(k))
                    mat.add(l)
        return mat

    def create_sampler(self, **kw):
        pass

    def create_camera(self, **kw):
        pass



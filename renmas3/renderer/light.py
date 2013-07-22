
from ..base import create_shader_function
from .mat import func_pointers_shader
from .surface import SurfaceShader
from .sunsky import SunSky

class AreaLight:
    def __init__(self, shape, material, col_mgr):
        self.shape = shape
        self.material = material
        self.col_mgr = col_mgr

    def prepare_illuminate(self, runtimes):
        #shader to caculate random point on shape
        code, props = self.shape.light_sample()
        sample_sh = SurfaceShader(code, props, col_mgr=self.col_mgr)
        sample_sh.prepare(runtimes)

        if self.material.emission is None:
            raise ValueError("Area light: Material doesn't have emission shader!")

        self.material.emission.prepare(runtimes)

        sample_name = sample_sh.method_name()
        emission_name = self.material.emission.method_name()

        line1 = "%s(hitpoint, shadepoint)\n" % sample_name
        line2 = "%s(hitpoint, shadepoint)\n" % emission_name 
        code = line1 + line2 + """
wi = shadepoint.shape_sample - hitpoint.hit
len_squared = wi[0] * wi[0] + wi[1] * wi[1] + wi[2] * wi[2]
wi = normalize(wi)

shp_normal = shadepoint.shape_normal * -1.0
cos_light = dot(shp_normal, wi)
if cos_light < 0.0:
    cos_light = 0.0

weight = cos_light / (shadepoint.shape_pdf * len_squared)
shadepoint.light_intensity = shadepoint.material_emission * weight
shadepoint.light_position = shadepoint.shape_sample
shadepoint.wi = wi
        """

        illuminate = SurfaceShader(code, props={}, col_mgr=self.col_mgr)
        illuminate.prepare(runtimes, [sample_sh.shader, self.material.emission.shader])
        name = illuminate.method_name()
        ptrs = [r.address_label(name) for r in runtimes]
        return ptrs

class Light:
    def __init__(self, illuminate):
        self.illuminate = illuminate

    def prepare_illuminate(self, runtimes):
        self.illuminate.prepare(runtimes)
        name = self.illuminate.method_name()
        ptrs = [r.address_label(name) for r in runtimes]
        return ptrs

class LightManager:
    def __init__(self):
        self._lights = []
        self._lights_d = {}
        self._environment = None

    def add(self, name, light):
        if name in self._lights_d:
            raise ValueError("Light with that name allready exist!")
        if not isinstance(light, (Light, AreaLight, SunSky)):
            raise ValueError("Type error. Light is expected!", light)
        #TODO -- implement check not to add environment light more than once
        if isinstance(light, SunSky):
            self._environment = light
        self._lights.append(light)
        self._lights_d[name] = light

    def prepare_environment(self, name, runtimes, col_mgr):
        if self._environment is not None:
            return self._environment.prepare_environment(name, runtimes)
        code = "shadepoint.light_intensity = spectrum(0.0)"
        illuminate = SurfaceShader(code, props={}, col_mgr=col_mgr,
                method_name=name)
        illuminate.prepare(runtimes, [])
        return illuminate.shader

    def remove(self, name):
        if name not in self._lights_d:
            raise ValueError("Light doesn't exist!")

        light = self._lights_d[name]
        del self._lights_d[name]
        self._lights.remove(light)

    def light_idx(self, name):
        if name not in self._lights_d:
            raise ValueError("Light doesn't exist!")
        light = self._lights_d[name]
        return self._lights.index(light)

    def prepare_illuminate(self, label, runtimes):
        shader = func_pointers_shader(label, runtimes,
                 self._lights, lambda light, run: light.prepare_illuminate(run))
        return shader

    def nlights_shader(self, label, runtimes):
        code = "return %i\n" % len(self._lights)
        bs = create_shader_function(label, code, [])
        bs.prepare(runtimes)
        return bs.shader

    def get_area_light(self, shape):
        for name, light in self._lights_d.items():
            if isinstance(light, AreaLight) and shape is light.shape:
                return name 
        return None


from ..base import create_shader_function
from .mat import func_pointers_shader

class Light:
    def __init__(self, illuminate=None, emit=None):
        self.illuminate = illuminate
        self.emit = emit

    def prepare_illuminate(self, runtimes):
        self.illuminate.prepare(runtimes)
        name = self.illuminate.method_name()
        ptrs = [r.address_label(name) for r in runtimes]
        return ptrs

    def prepare_emit(self, runtimes):
        self.emit.prepare(runtimes)
        name = self.emit.method_name()
        ptrs = [r.address_label(name) for r in runtimes]
        return ptrs

class LightManager:
    def __init__(self):
        self._lights = []
        self._lights_d = {}

    def add(self, name, light):
        if name in self._lights_d:
            raise ValueError("Light with that name allready exist!")
        if not isinstance(light, Light):
            raise ValueError("Type error. Light is expected!", light)
        self._lights.append(light)
        self._lights_d[name] = light

    def remove(self, name):
        pass

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



import os.path
from sdl import Vector3, Loader, parse_args, Vec3Arg, FloatArg,\
    Ray, StructArgPtr, Shader, StructArg, RGBSpectrum, RGBArg,\
    SampledSpectrum, SampledArg, IntArg
from sdl.arr import PtrsArray, ArrayArg

from .hitpoint import HitPoint
from .shadepoint import ShadePoint


class Light:
    pass


class GeneralLight(Light):
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'light_shaders')
        self._loader = Loader([path])
        self.shader = None

    def _func_args(self, spectrum):

        wo = Vector3(0.0, 0.0, 0.0)
        wi = Vector3(0.0, 0.0, 0.0)
        li = spectrum.zero()
        lpos = Vector3(0.0, 0.0, 0.0)
        ref = spectrum.zero()

        hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                      Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
        sp = ShadePoint(wo, wi, li, lpos, ref, 0.0)

        func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sp)]
        return func_args

    def load(self, shader_name, sam_mgr, spectral=False):
        tmp_args = []
        text = self._loader.load(shader_name, 'props.txt')
        if text is not None:
            tmp_args = parse_args(text)
        args = []
        for a in tmp_args:
            if spectral and isinstance(a, RGBArg):
                val = sam_mgr.rgb_to_sampled(a.value, illum=True)
                aa = SampledArg(a.name, val)
                args.append(aa)
            elif not spectral and isinstance(a, SampledArg):
                val = sam_mgr.sampled_to_rgb(a.value)
                aa = RGBArg(a.name, val)
                args.append(aa)
            else:
                args.append(a)

        
        code = self._loader.load(shader_name, 'code.py')
        if code is None:
            raise ValueError("code.py in %s shader dont exist!" % shader_name)
        
        name = 'light_%i' % id(args)
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        self.shader = Shader(code=code, args=args, name=name,
                             func_args=func_args, is_func=True)
        self._spectral = spectral
        self._sam_mgr = sam_mgr

    def compile(self, shaders=[]):
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

    def set_value(self, name, val):
        if self.shader is None:
            raise ValueError("Light shader is not loaded!")
        if self._spectral and isinstance(val, RGBSpectrum):
            val = self._sam_mgr.rgb_to_sampled(val, illum=True)
        if not self._spectral and isinstance(val, SampledSpectrum):
            val = self._sam_mgr.sampled_to_rgb(val)
        self.shader.set_value(name, val)


class AreaLight(Light):
    def __init__(self, shape, material):
        # sample on shape
        # emission on material
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'area_light_shaders')
        self._loader = Loader([path])


class EnvironmentLight(Light):
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'environment_light_shaders')
        self._loader = Loader([path])


class LightManager:
    def __init__(self):
        self._lights = []
        self._lights_d = {}
        self._environment = None

    def add(self, name, light):
        if name in self._lights_d:
            raise ValueError("Light %s allready exist!" % name)
        if not isinstance(light, Light):
            raise ValueError("Type error. Light is expected!", light)

        #TODO -- implement check not to add environment light more than once
        self._lights.append(light)
        self._lights_d[name] = light

    def remove(self, name):
        if name not in self._lights_d:
            raise ValueError("Light %s doesn't exist!" % name)

        light = self._lights_d[name]
        del self._lights_d[name]
        self._lights.remove(light)

    def light_idx(self, name):
        if name not in self._lights_d:
            raise ValueError("Light %s doesn't exist!" % name)

        light = self._lights_d[name]
        return self._lights.index(light)

    def _func_args(self, spectrum):

        wo = Vector3(0.0, 0.0, 0.0)
        wi = Vector3(0.0, 0.0, 0.0)
        li = spectrum.zero()
        lpos = Vector3(0.0, 0.0, 0.0)
        ref = spectrum.zero()

        hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                      Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
        sp = ShadePoint(wo, wi, li, lpos, ref, 0.0)

        func_args = [StructArgPtr('hitpoint', hp),
                     StructArgPtr('shadepoint', sp), IntArg('mat_idx', 0)]
        return func_args

    def _lgt_radiance(self, sam_mgr, spectral=False):
        code = """
ptr_func = lgt_ptrs[mat_idx]
#light_radiance(hitpoint, shadepoint, ptr_func)
        """
        lgt_ptrs = ArrayArg('lgt_ptrs', PtrsArray())
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        args = [lgt_ptrs]
        self.rad_shader = Shader(code=code, args=args, name='lgt_radiance',
                        func_args=func_args, is_func=True)

    def compile_shaders(self, sam_mgr, spectral=False, shaders=[]):

        for l in self._lights:
            l.compile(shaders)
        self._lgt_radiance(sam_mgr, spectral)
        self.rad_shader.compile(shaders)


    def prepare_shaders(self, runtimes):
        pass

    def compile(self, shaders=[]):
        pass
        #self.shader.compile(shaders)

    def prepare(self, runtimes):
        pass
        #self.shader.prepare(runtimes)


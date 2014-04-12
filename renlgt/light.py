
import os.path
from sdl import Loader, parse_args, StructArgPtr, Shader,\
    RGBSpectrum, RGBArg, SampledSpectrum, SampledArg, IntArg,\
    ArgList, PointerArg
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
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]
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

    def get_value(self, name):
        if self.shader is None:
            raise ValueError("Light shader is not loaded!")
        return self.shader.get_value(name)

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

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'area_light_shaders')
        self._loader = Loader([path])

        self.shape = shape
        self.material = material
        self.shader = None

    def _func_args(self, spectrum):
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]
        return func_args

    def _load_args(self):
        tmp_args = []
        text = self._loader.load(self._shader_name, 'props.txt')
        if text is not None:
            tmp_args = parse_args(text)
        args = []
        for a in tmp_args:
            if self._spectral and isinstance(a, RGBArg):
                val = self._sam_mgr.rgb_to_sampled(a.value, illum=True)
                aa = SampledArg(a.name, val)
                args.append(aa)
            elif not self._spectral and isinstance(a, SampledArg):
                val = self._sam_mgr.sampled_to_rgb(a.value)
                aa = RGBArg(a.name, val)
                args.append(aa)
            else:
                args.append(a)
        return args

    def load(self, shader_name, sam_mgr, spectral=False):
        self._spectral = spectral
        self._sam_mgr = sam_mgr
        self._shader_name = shader_name

        args = self._load_args()

        ptr_lgt_sample = PointerArg('ptr_light_sample', 0)
        lgt_sample = ArgList('ptr_light_sample', [ptr_lgt_sample])
        args.append(lgt_sample)
        ptr_mat_emission = PointerArg('ptr_mat_emission', 0)
        mat_emission = ArgList('ptr_mat_emission', [ptr_mat_emission])
        args.append(mat_emission)

        code = self._loader.load(shader_name, 'code.py')
        if code is None:
            raise ValueError("code.py in %s shader dont exist!" % shader_name)

        name = 'light_%i' % id(args)
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        self.shader = Shader(code=code, args=args, name=name,
                             func_args=func_args, is_func=True)
        
        # area light emission shader
        name = 'light_emission%i' % id(args)
        func_args = self._func_args(s)
        args = []
        ptr_lgt_pdf = PointerArg('ptr_light_pdf', 0)
        lgt_pdf = ArgList('ptr_light_pdf', [ptr_lgt_pdf])
        args.append(lgt_pdf)
        ptr_mat_emission = PointerArg('ptr_mat_emission', 0)
        mat_emission = ArgList('ptr_mat_emission', [ptr_mat_emission])
        args.append(mat_emission)
        code = """
__light_pdf(hitpoint, shadepoint, ptr_light_pdf)
__material_emission(hitpoint, shadepoint, ptr_mat_emission)
        """
        self.emission_shader = Shader(code=code, args=args, name=name,
                                      func_args=func_args, is_func=True)

    def compile(self, shaders=[]):
        self.shader.compile(shaders)
        self.emission_shader.compile(shaders)

        s = self._sam_mgr.zero() if self._spectral else RGBSpectrum(0.0, 0.0, 0.0)
        self.light_sample_shader = self.shape.light_sample(s)
        self.light_sample_shader.compile(shaders)

        self.light_pdf_shader = self.shape.light_pdf(s)
        self.light_pdf_shader.compile(shaders)

        self._emission_shader = self.material.emission_shader()
        self._emission_shader.compile(shaders)


    def prepare(self, runtimes):
        self.light_sample_shader.prepare(runtimes)
        ptrs = self.light_sample_shader.get_ptrs()
        args = [PointerArg('ptr_light_sample', p) for p in ptrs]
        lgt_sample = self.shader._get_arg('ptr_light_sample')
        lgt_sample.resize(args)

        self.light_pdf_shader.prepare(runtimes)
        ptrs = self.light_pdf_shader.get_ptrs()
        args = [PointerArg('ptr_light_pdf', p) for p in ptrs]
        lgt_pdf = self.emission_shader._get_arg('ptr_light_pdf')
        lgt_pdf.resize(args)

        self._emission_shader.prepare(runtimes)
        self.material.sync_shader_props(self._emission_shader)
        ptrs = self._emission_shader.get_ptrs()
        args = [PointerArg('ptr_mat_emission', p) for p in ptrs]
        ptr_emission = self.shader._get_arg('ptr_mat_emission')
        ptr_emission.resize(args)

        args = [PointerArg('ptr_mat_emission', p) for p in ptrs]
        ptr_emission = self.emission_shader._get_arg('ptr_mat_emission')
        ptr_emission.resize(args)

        self.shader.prepare(runtimes)
        self.emission_shader.prepare(runtimes)

    def get_value(self, name):
        if self.shader is None:
            raise ValueError("Light shader is not loaded!")
        return self.shader.get_value(name)

    def set_value(self, name, val):
        if self.shader is None:
            raise ValueError("Light shader is not loaded!")
        if self._spectral and isinstance(val, RGBSpectrum):
            val = self._sam_mgr.rgb_to_sampled(val, illum=True)
        if not self._spectral and isinstance(val, SampledSpectrum):
            val = self._sam_mgr.sampled_to_rgb(val)
        self.shader.set_value(name, val)


class EnvironmentLight(Light):
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'environment_light_shaders')
        self._loader = Loader([path])


class LightManager:
    def __init__(self):
        self._lights = []
        self._lights_d = {}
        self._env_light = None
        self.env_shader = None

    def add(self, name, light):
        if name in self._lights_d:
            raise ValueError("Light %s allready exist!" % name)
        if not isinstance(light, Light):
            raise ValueError("Type error. Light is expected!", light)

        #TODO -- implement check not to add environment light more than once
        self._lights.append(light)
        self._lights_d[name] = light

    def remove(self, name=None, light=None):
        if name is None and light is None:
            raise ValueError("Name or Light argument is required")

        if name is not None and name not in self._lights_d:
            raise ValueError("Light %s doesn't exist!" % name)

        if name is not None:
            light = self._lights_d[name]
            del self._lights_d[name]
            self._lights.remove(light)
        elif light is not None:
            for name in self._lights_d.keys():
                if light is self._lights_d[name]:
                    del self._lights_d[name]
                    self._lights.remove(light)

    def light_idx(self, name):
        if name not in self._lights_d:
            raise ValueError("Light %s doesn't exist!" % name)

        light = self._lights_d[name]
        return self._lights.index(light)

    def _func_args(self, spectrum):
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum)),
                     IntArg('mat_idx', 0)]
        return func_args

    def _lgt_radiance(self, sam_mgr, spectral=False):
        code = """
ptr_func = lgt_ptrs[mat_idx]
__light_radiance(hitpoint, shadepoint, ptr_func)
        """
        lgt_ptrs = ArrayArg('lgt_ptrs', PtrsArray())
        al = ArgList('lgt_ptrs', [lgt_ptrs])
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        args = [al]
        self.rad_shader = Shader(code=code, args=args, name='light_radiance',
                                 func_args=func_args, is_func=True)

    def _lgt_emission(self, sam_mgr, spectral=True):
        code = """
if light_id < 0:
    shadepoint.light_intensity = Spectrum(0.0)
    shadepoint.light_pdf = 1.0
else:
    ptr_func = lgt_ptrs[light_id]
    __light_emission(hitpoint, shadepoint, ptr_func)
        """
        lgt_ptrs = ArrayArg('lgt_ptrs', PtrsArray())
        al = ArgList('lgt_ptrs', [lgt_ptrs])
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(s)),
                     IntArg('light_id', -1)]
        args = [al]
        self.emission_shader = Shader(code=code, args=args, name='light_emission',
                                      func_args=func_args, is_func=True)

    def compile_shaders(self, sam_mgr, spectral=False, shaders=[]):

        for l in self._lights:
            l.compile(shaders)
        self._lgt_radiance(sam_mgr, spectral)
        self.rad_shader.compile(shaders)

        self._lgt_emission(sam_mgr, spectral)
        self.emission_shader.compile(shaders)

        code = "return %i\n" % len(self._lights)
        self.nlights_shader = Shader(code=code, name='number_of_lights',
                                     is_func=True)
        self.nlights_shader.compile()

        self._compile_environment(sam_mgr, spectral, shaders)

    def _compile_environment(self, sam_mgr, spectral, shaders=[]):
        if self._env_light is not None:
            self.env_shader = self._env_light.env_shader()
            self.env_shader.compile(shaders)
            return

        # We create dummy shader for environment emission
        code = '''
shadepoint.light_intensity = Spectrum(0.0)
shadepoint.light_pdf = 1.0
        '''
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(s))]
        self.env_shader = Shader(code=code, name='environment_emission',
                                 func_args=func_args, is_func=True)
        self.env_shader.compile(shaders)

    def prepare_shaders(self, runtimes):
        for l in self._lights:
            l.prepare(runtimes)

        ptrs = []
        for l in self._lights:
            p = l.shader.get_ptrs()
            ptrs.append(p)
        args = []
        for i in range(len(runtimes)):
            pa = PtrsArray()
            for v in ptrs:
                pa.append(v[i])
            args.append(ArrayArg('lgt_ptrs', pa))

        aal = self.rad_shader._get_arg('lgt_ptrs')
        aal.resize(args)
        self.rad_shader.prepare(runtimes)

        self.nlights_shader.prepare(runtimes)
        self.env_shader.prepare(runtimes)

        ##### emission shader
        ptrs = []
        for l in self._lights:
            if isinstance(l, AreaLight):
                p = l.emission_shader.get_ptrs()
                ptrs.append(p)
        args = []
        for i in range(len(runtimes)):
            pa = PtrsArray()
            for v in ptrs:
                pa.append(v[i])
            args.append(ArrayArg('lgt_ptrs', pa))
        aal = self.emission_shader._get_arg('lgt_ptrs')
        aal.resize(args)
        self.emission_shader.prepare(runtimes)
        self.update_light_ids()

    def update_light_ids(self):
        idx = 0
        for l in self._lights:
            if isinstance(l, AreaLight):
                l.shape.light_id = idx
                idx += 1

    def shapes_to_update(self):
        shapes = []
        for l in self._lights:
            if isinstance(l, AreaLight):
                shapes.append(l.shape)
        return shapes

    def arealight(self, shape):
        for light in self._lights:
            if isinstance(light, AreaLight) and light.shape is shape:
                return light
        return None

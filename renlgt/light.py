
import os.path
from sdl import Loader, StructArgPtr, Shader,\
    RGBSpectrum, RGBArg, SampledSpectrum, SampledArg, IntArg,\
    ArgList, PointerArg, Vector3
from sdl.arr import PtrsArray, ArrayArg

from .hitpoint import HitPoint
from .shadepoint import ShadePoint
from .parse_args import parse_args


def output_arg(name, value):
    if isinstance(value, int):
        return '%s = %i\n' % (name, value)
    elif isinstance(value, float):
        return '%s = %f\n' % (name, value)
    elif isinstance(value, RGBSpectrum):
        return '%s = %f, %f, %f\n' % (name, value.r, value.g, value.b)
    elif isinstance(value, Vector3):
        return '%s = %f, %f, %f\n' % (name, value.x, value.y, value.z)
    else:
        raise ValueError("Unsupported otuput to save ", name, value)


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


    def load(self, shader_name, color_mgr):
        args = []
        text = self._loader.load(shader_name, 'props.txt')
        if text is not None:
            args = parse_args(text, color_mgr)

        code = self._loader.load(shader_name, 'code.py')
        if code is None:
            raise ValueError("code.py in %s shader dont exist!" % shader_name)

        name = 'light_%i' % id(args)
        func_args = self._func_args(color_mgr.zero())
        self.shader = Shader(code=code, args=args, name=name,
                             func_args=func_args, is_func=True)
        self._color_mgr = color_mgr
        self._shader_name = shader_name

    def compile(self, shaders=[]):
        self.shader.compile(shaders, color_mgr=self._color_mgr)

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

    def get_value(self, name):
        if self.shader is None:
            raise ValueError("Light shader is not loaded!")
        return self.shader.get_value(name)

    def set_value(self, name, val):
        if self.shader is None:
            raise ValueError("Light shader is not loaded!")
        if isinstance(val, (RGBSpectrum, SampledSpectrum)):
            val = self._color_mgr.convert_spectrum(val, illum=True)
        self.shader.set_value(name, val)

    def output(self, name):
        txt ='Light\n'
        txt +='type = %s\n' % self._shader_name 
        txt +='name = %s\n' % name

        args = []
        text = self._loader.load(self._shader_name, 'props.txt')
        if text is not None:
            args = parse_args(text)
        for arg in args:
            value = self.get_value(arg.name)
            txt += output_arg(arg.name, value)
        txt +='End\n'
        return txt


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
        args = []
        text = self._loader.load(self._shader_name, 'props.txt')
        if text is not None:
            args = parse_args(text, self._color_mgr)
        return args

    def load(self, shader_name, color_mgr):
        self._color_mgr = color_mgr
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
        func_args = self._func_args(color_mgr.zero())
        self.shader = Shader(code=code, args=args, name=name,
                             func_args=func_args, is_func=True)
        
        # area light emission shader
        name = 'light_emission%i' % id(args)
        func_args = self._func_args(color_mgr.zero())
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
        self.shader.compile(shaders, color_mgr=self._color_mgr)
        self.emission_shader.compile(shaders, color_mgr=self._color_mgr)

        spec = self._color_mgr.zero()
        self.light_sample_shader = self.shape.light_sample(spec)
        self.light_sample_shader.compile(shaders, color_mgr=self._color_mgr)

        self.light_pdf_shader = self.shape.light_pdf(spec)
        self.light_pdf_shader.compile(shaders, color_mgr=self._color_mgr)

        self._emission_shader = self.material.emission_shader()
        self._emission_shader.compile(shaders, color_mgr=self._color_mgr)


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
        if isinstance(val, (RGBSpectrum, SampledSpectrum)):
            val = self._color_mgr.convert_spectrum(val, illum=True)
        self.shader.set_value(name, val)


class EnvironmentLight(Light):
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'env_shaders')
        self._loader = Loader([path])

    def _func_args(self, spectrum):
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]
        return func_args

    def load(self, shader_name, color_mgr):
        self._color_mgr = color_mgr
        self._shader_name = shader_name

        args = []
        text = self._loader.load(shader_name, 'props.txt')
        if text is not None:
            args = parse_args(text, color_mgr)

        code = self._loader.load(shader_name, 'env.py')
        if code is None:
            raise ValueError("env.py in %s shader dont exist!" % shader_name)

        name = 'env_light_%i' % id(args)
        func_args = self._func_args(color_mgr.zero())
        self.env_shader = Shader(code=code, args=args, name='environment_emission',
                                 func_args=func_args, is_func=True)

    def get_value(self, name):
        if self.env_shader is None:
            raise ValueError("Environment shader is not loaded!")
        return self.env_shader.get_value(name)

    def set_value(self, name, val):
        if self.env_shader is None:
            raise ValueError("Environment shader is not loaded!")
        if isinstance(val, (RGBSpectrum, SampledSpectrum)):
            val = self._color_mgr.convert_spectrum(val, illum=True)
        self.env_shader.set_value(name, val)


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
        if isinstance(light, EnvironmentLight):
            self._env_light = light
        else:
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

    def _lgt_radiance(self, color_mgr):
        code = """
ptr_func = lgt_ptrs[mat_idx]
__light_radiance(hitpoint, shadepoint, ptr_func)
        """
        lgt_ptrs = ArrayArg('lgt_ptrs', PtrsArray())
        al = ArgList('lgt_ptrs', [lgt_ptrs])
        func_args = self._func_args(color_mgr.zero())
        args = [al]
        self.rad_shader = Shader(code=code, args=args, name='light_radiance',
                                 func_args=func_args, is_func=True)

    def _lgt_emission(self, color_mgr):
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
        spec = color_mgr.zero()
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spec)),
                     IntArg('light_id', -1)]
        args = [al]
        self.emission_shader = Shader(code=code, args=args, name='light_emission',
                                      func_args=func_args, is_func=True)

    def compile_shaders(self, color_mgr, shaders=[]):

        for l in self._lights:
            l.compile(shaders)
        self._lgt_radiance(color_mgr)
        self.rad_shader.compile(shaders, color_mgr=color_mgr)

        self._lgt_emission(color_mgr)
        self.emission_shader.compile(shaders, color_mgr=color_mgr)

        code = "return %i\n" % len(self._lights)
        self.nlights_shader = Shader(code=code, name='number_of_lights',
                                     is_func=True)
        self.nlights_shader.compile()

        self._compile_environment(color_mgr, shaders)

    def _compile_environment(self, color_mgr, shaders=[]):
        if self._env_light is not None:
            self.env_shader = self._env_light.env_shader
            self.env_shader.compile(shaders, color_mgr=color_mgr)
            return

        # We create dummy shader for environment emission
        code = '''
shadepoint.light_intensity = Spectrum(0.0)
shadepoint.light_pdf = 1.0
        '''
        spec = color_mgr.zero()
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spec))]
        self.env_shader = Shader(code=code, name='environment_emission',
                                 func_args=func_args, is_func=True)
        self.env_shader.compile(shaders, color_mgr=color_mgr)

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

    def output(self):
        txt = ''
        for name, light in self._lights_d.items():
            if isinstance(light, AreaLight):
                continue
            txt += light.output(name) + '\n'
        return txt

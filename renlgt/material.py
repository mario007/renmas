
import os.path
from sdl import Vector3, Loader, parse_args, Vec3Arg, FloatArg,\
    Ray, StructArgPtr, Shader, StructArg, RGBSpectrum, RGBArg,\
    SampledSpectrum, SampledArg, IntArg, ArgList
from sdl.arr import PtrsArray, ArrayArg

from .hitpoint import HitPoint
from .shadepoint import ShadePoint


class Material:
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'mat_shaders')
        self._loader = Loader([path])

        self._bsdf_shader = None

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

        code = self._loader.load(shader_name, 'bsdf.py')
        if code is None:
            raise ValueError("bsdf.py in %s shader dont exist!" % shader_name)
        
        name = 'material_%i' % id(args)
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        self._bsdf_shader = Shader(code=code, args=args, name=name,
                                   func_args=func_args, is_func=True)
        self._spectral = spectral
        self._sam_mgr = sam_mgr

    def compile(self, shaders=[]):
        self._bsdf_shader.compile(shaders)

    def prepare(self, runtimes):
        self._bsdf_shader.prepare(runtimes)

    def set_value(self, name, val):
        if self._bsdf_shader is None:
            raise ValueError("Light shader is not loaded!")
        if self._spectral and isinstance(val, RGBSpectrum):
            val = self._sam_mgr.rgb_to_sampled(val, illum=True)
        if not self._spectral and isinstance(val, SampledSpectrum):
            val = self._sam_mgr.sampled_to_rgb(val)
        self._bsdf_shader.set_value(name, val)

    def get_value(self, name):
        if self._bsdf_shader is None:
            raise ValueError("Material shader is not loaded!")
        return self._bsdf_shader.get_value(name)


class MaterialManager:
    def __init__(self):
        self._materials = []
        self._materials_d = {}

    def add(self, name, material):
        if name in self._materials_d:
            raise ValueError("Material %s allready exist!" % name)
        if not isinstance(material, Material):
            raise ValueError("Type error. Material is expected!", material)

        self._materials.append(material)
        self._materials_d[name] = material

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

    def _mtl_reflectance(self, sam_mgr, spectral=False):
        code = """
ptr_func = mtl_ptrs[mat_idx]
__material_reflectance(hitpoint, shadepoint, ptr_func)
        """
        lgt_ptrs = ArrayArg('mtl_ptrs', PtrsArray())
        al = ArgList('mtl_ptrs', [lgt_ptrs])
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        args = [al]
        self.ref_shader = Shader(code=code, args=args, name='material_reflectance',
                                 func_args=func_args, is_func=True)

    def compile_shaders(self, sam_mgr, spectral=False, shaders=[]):

        for m in self._materials:
            m.compile(shaders)
        self._mtl_reflectance(sam_mgr, spectral)
        self.ref_shader.compile(shaders)

    def prepare_shaders(self, runtimes):
        ptrs = []
        for m in self._materials:
            m.prepare(runtimes)
            p = m._bsdf_shader.get_ptrs()
            ptrs.append(p)
        args = []
        for i in range(len(runtimes)):
            pa = PtrsArray()
            for v in ptrs:
                pa.append(v[i])
            args.append(ArrayArg('mtl_ptrs', pa))
        
        aal = self.ref_shader._get_arg('mtl_ptrs')
        aal.resize(args)
        self.ref_shader.prepare(runtimes)

    def index(self, name):
        if name not in self._materials_d:
            raise ValueError("Material %s doesn't exist!" % name)
        m = self._materials_d[name]
        return self._materials.index(m)

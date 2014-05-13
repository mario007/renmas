
import os.path
from sdl import Vector3, Loader, parse_args, Vec3Arg, FloatArg,\
    Ray, StructArgPtr, Shader, StructArg, RGBSpectrum, RGBArg,\
    SampledSpectrum, SampledArg, IntArg, ArgList, PointerArg
from sdl.arr import PtrsArray, ArrayArg

from .hitpoint import HitPoint
from .shadepoint import ShadePoint


def output_arg(name, value):
    if isinstance(value, int):
        return '%s = %i\n' % (name, value)
    elif isinstance(value, float):
        return '%s = %f\n' % (name, value)
    elif isinstance(value, RGBSpectrum):
        return '%s = %f, %f, %f\n' % (name, value.r, value.g, value.b)
    else:
        raise ValueError("Unsupported otuput to save ", name, value)


class Material:
    def __init__(self):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'mat_shaders')
        self._loader = Loader([path])

        self._bsdf_shader = None
        self._sampling_shader = None
        self._shader_name = None

    def is_emissive(self):
        if self._shader_name is None:
            return False
        return self._loader.exist(self._shader_name, 'emission.py')

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

        code = self._loader.load(shader_name, 'bsdf.py')
        if code is None:
            raise ValueError("bsdf.py in %s doesnt exist!" % shader_name)
        
        args = self._load_args()
        name = 'material_%i' % id(args)
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        self._bsdf_shader = Shader(code=code, args=args, name=name,
                                   func_args=func_args, is_func=True)

        #Sampling shader
        code = self._loader.load(self._shader_name, 'sample.py')
        if code is None:
            code = self._default_sampling()

        args = self._load_args()
        ptr_mat_bsdf = PointerArg('ptr_mat_bsdf', 0)
        ptr_mat_pdf = PointerArg('ptr_mat_pdf', 0)
        ptr_bsdf = ArgList('ptr_mat_bsdf', [ptr_mat_bsdf])
        ptr_pdf = ArgList('ptr_mat_pdf', [ptr_mat_pdf])
        args.append(ptr_bsdf)
        args.append(ptr_pdf)

        name = 'material_sampling_%i' % id(args)
        func_args = self._func_args(s)
        self._sampling_shader = Shader(code=code, args=args, name=name,
                                       func_args=func_args, is_func=True)

        #material pdf
        code = self._loader.load(self._shader_name, 'pdf.py')
        if code is None:
            code = self._default_pdf()
        args = self._load_args()
        name = 'material_pdf_%i' % id(args)
        func_args = self._func_args(s)
        self._pdf_shader = Shader(code=code, args=args, name=name,
                                  func_args=func_args, is_func=True)


    def _default_sampling(self):
        code = """
r1 = random()
r2 = random()
e = 1.0

phi = 2.0 * 3.14159 * r1
exponent = 1.0 / (e + 1.0)
cos_theta = pow(r2, exponent)

tmp = 1.0 - cos_theta * cos_theta
sin_theta = sqrt(tmp)
sin_phi = sin(phi)
cos_phi = cos(phi)
pu = sin_theta * cos_phi 
pv = sin_theta * sin_phi
pw = cos_theta

w = hitpoint.normal 
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)

ndir = u * pu + v * pv + w * pw
shadepoint.wi = normalize(ndir)

__material_pdf(hitpoint, shadepoint, ptr_mat_pdf)
__material_reflectance(hitpoint, shadepoint, ptr_mat_bsdf)
        """
        return code

    def _default_pdf(self):
        code = """
shadepoint.pdf = dot(hitpoint.normal, shadepoint.wi) * 0.318309886
        """
        return code

    def compile(self, shaders=[]):
        self._bsdf_shader.compile(shaders)
        self._sampling_shader.compile(shaders)
        self._pdf_shader.compile(shaders)

    def prepare(self, runtimes):
        self._bsdf_shader.prepare(runtimes)
        self._pdf_shader.prepare(runtimes)

        ptrs = self._bsdf_shader.get_ptrs()
        args = [PointerArg('ptr_mat_bsdf', p) for p in ptrs]
        ptr_bsdf = self._sampling_shader._get_arg('ptr_mat_bsdf')
        ptr_bsdf.resize(args)

        ptrs = self._pdf_shader.get_ptrs()
        args = [PointerArg('ptr_mat_pdf', p) for p in ptrs]
        ptr_pdf = self._sampling_shader._get_arg('ptr_mat_pdf')
        ptr_pdf.resize(args)

        self._sampling_shader.prepare(runtimes)

    def emission_shader(self, shaders=[]):
        args = self._load_args()
        code = self._loader.load(self._shader_name, 'emission.py')
        if code is None:
            raise ValueError("emission.py in %s dont exist!" % self._shader_name)

        name = 'material_emission_%i' % id(args)
        s = self._sam_mgr.zero() if self._spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        emission_shader = Shader(code=code, args=args, name=name,
                                 func_args=func_args, is_func=True)
        return emission_shader

    def sync_shader_props(self, shader):
        for arg in shader.args:
            val = self.get_value(arg.name)
            shader.set_value(arg.name, val)

    def set_value(self, name, val):
        if self._bsdf_shader is None:
            raise ValueError("Material shader is not loaded!")
        if self._spectral and isinstance(val, RGBSpectrum):
            val = self._sam_mgr.rgb_to_sampled(val, illum=False)
        if not self._spectral and isinstance(val, SampledSpectrum):
            val = self._sam_mgr.sampled_to_rgb(val)
        self._bsdf_shader.set_value(name, val)
        self._sampling_shader.set_value(name, val)

    def get_value(self, name):
        if self._bsdf_shader is None:
            raise ValueError("Material shader is not loaded!")
        return self._bsdf_shader.get_value(name)

    def output(self, name):
        txt = 'Material\n'
        txt += 'type = %s\n' % self._shader_name
        txt += 'name = %s\n' % name
        args = self._load_args()
        for arg in args:
            value = self.get_value(arg.name)
            txt += output_arg(arg.name, value)
        txt += 'End\n'
        return txt


class MaterialManager:
    def __init__(self):
        self._materials = []
        self._materials_d = {}
        self._materials_idx = {}

    def add(self, name, material):
        if name in self._materials_d:
            raise ValueError("Material %s allready exist!" % name)
        if not isinstance(material, Material):
            raise ValueError("Type error. Material is expected!", material)

        self._materials_idx[len(self._materials)] = name 
        self._materials.append(material)
        self._materials_d[name] = material

    def _func_args(self, spectrum):
        func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                     StructArgPtr('shadepoint', ShadePoint.factory(spectrum)),
                     IntArg('mat_idx', 0)]
        return func_args

    def _mtl_reflectance(self, sam_mgr, spectral=False):
        code = """
ptr_func = mtl_ptrs[mat_idx]
__material_reflectance(hitpoint, shadepoint, ptr_func)
        """
        ref_ptrs = ArrayArg('mtl_ptrs', PtrsArray())
        al = ArgList('mtl_ptrs', [ref_ptrs])
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        args = [al]
        self.ref_shader = Shader(code=code, args=args, name='material_reflectance',
                                 func_args=func_args, is_func=True)

    def _mtl_sampling(self, sam_mgr, spectral=False):
        code = """
ptr_func = mtl_sampling_ptrs[mat_idx]
__material_sampling(hitpoint, shadepoint, ptr_func)
        """
        sampling_ptrs = ArrayArg('mtl_sampling_ptrs', PtrsArray())
        al = ArgList('mtl_sampling_ptrs', [sampling_ptrs])
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        args = [al]
        self.sampling_shader = Shader(code=code, args=args, name='material_sampling',
                                 func_args=func_args, is_func=True)

    def _mtl_pdf(self, sam_mgr, spectral=False):
        code = """
ptr_func = mtl_pdf_ptrs[mat_idx]
__material_pdf(hitpoint, shadepoint, ptr_func)
        """
        pdf_ptrs = ArrayArg('mtl_pdf_ptrs', PtrsArray())
        al = ArgList('mtl_pdf_ptrs', [pdf_ptrs])
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        func_args = self._func_args(s)
        args = [al]
        self.pdf_shader = Shader(code=code, args=args, name='material_pdf',
                                 func_args=func_args, is_func=True)

    def compile_shaders(self, sam_mgr, spectral=False, shaders=[]):

        for m in self._materials:
            m.compile(shaders)

        self._mtl_reflectance(sam_mgr, spectral)
        self.ref_shader.compile(shaders)

        self._mtl_sampling(sam_mgr, spectral)
        self.sampling_shader.compile(shaders)

        self._mtl_pdf(sam_mgr, spectral)
        self.pdf_shader.compile(shaders)

    def prepare_shaders(self, runtimes):
        for m in self._materials:
            m.prepare(runtimes)

        args = self._pointer_args('_bsdf_shader', 'mtl_ptrs', runtimes)
        aal = self.ref_shader._get_arg('mtl_ptrs')
        aal.resize(args)
        self.ref_shader.prepare(runtimes)

        args = self._pointer_args('_sampling_shader', 'mtl_sampling_ptrs', runtimes)
        aal = self.sampling_shader._get_arg('mtl_sampling_ptrs')
        aal.resize(args)
        self.sampling_shader.prepare(runtimes)

        args = self._pointer_args('_pdf_shader', 'mtl_pdf_ptrs', runtimes)
        aal = self.pdf_shader._get_arg('mtl_pdf_ptrs')
        aal.resize(args)
        self.pdf_shader.prepare(runtimes)

    def _pointer_args(self, shader_name, arg_name, runtimes):
        ptrs = []
        for m in self._materials:
            shader = getattr(m, shader_name)
            p = shader.get_ptrs()
            ptrs.append(p)

        args = []
        for i in range(len(runtimes)):
            pa = PtrsArray()
            for v in ptrs:
                pa.append(v[i])
            args.append(ArrayArg(arg_name, pa))
        return args

    def index(self, name):
        if name not in self._materials_d:
            raise ValueError("Material %s doesn't exist!" % name)
        m = self._materials_d[name]
        return self._materials.index(m)

    def material(self, index=None, name=None):
        if index is None and name is None:
            raise ValueError("Index or Name of material is required")

        if name is not None:
            return self._materials_d[name] 

        return self._materials[index]

    def name(self, index):
        return self._materials_idx[index]

    def output(self):
        txt = ''
        for index, mat in enumerate(self._materials):
            txt += mat.output(self.name(index)) + '\n'
        return txt

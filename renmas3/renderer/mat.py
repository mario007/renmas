import platform
import collections
from ..base import Spectrum, Vec3, Float, Integer, arg_list, arg_map, Shader
from ..shapes import HitPoint
from .surface import ShadePoint, SurfaceShader

def func_pointers_shader(label, runtimes, objs, prepare):
    pointers = collections.defaultdict(list)
    for obj in objs:
        p = prepare(obj, runtimes)
        for adr, r in zip(p, runtimes):
            pointers[id(r)].append(adr)

    bits = platform.architecture()[0]
    # eax=hitpoint, ebx=shadepoint, ecx=index
    code = "#DATA \n"
    if len(objs) > 0:
        if bits == '64bit':
            code += "uint64 func_pointers[%i] \n" % len(objs)
        else:
            code += "uint32 func_pointers[%i] \n" % len(objs)
    code += "#CODE \n"
    code += "global %s:\n" % label
    if len(objs) > 0:
        if bits == '64bit':
            code += "mov rdx, func_pointers\n"
            code += "call qword [rdx + 8*rcx]\n" 
        else:
            code += "mov edx, func_pointers\n"
            code += "call dword [edx + 4*ecx]\n" 
    code += "ret\n"
    ret_type = Integer
    args = arg_map([])
    in_args = arg_list([('hitpoint', HitPoint), ('shadepoint', ShadePoint),
        ('index', Integer)])
    shader = Shader(label, code, args, input_args=in_args, ret_type=ret_type,
            func=True, functions={})

    shader.prepare(runtimes)
    if len(objs) > 0:
        for ds, r in zip(shader._ds, runtimes):
            ds['func_pointers'] = tuple(pointers[id(r)])
    return shader

class Material:
    def __init__(self, bsdf=None, sample=None, pdf=None, emission=None, is_dielectric=False):
        self.bsdf = bsdf
        self.sample = sample
        self.pdf = pdf
        self.emission = emission
        self.is_dielectric = is_dielectric

    def prepare_bsdf(self, runtimes):
        self.bsdf.prepare(runtimes)
        name = self.bsdf.method_name()
        bsdf_ptrs = [r.address_label(name) for r in runtimes]
        return bsdf_ptrs

    def prepare_sample(self, runtimes):
        if self.sample is None:
            raise ValueError("Create default(lambertian) sample if it is not specified")
        self.sample.prepare(runtimes)
        name = self.sample.method_name()
        sample_ptrs = [r.address_label(name) for r in runtimes]
        return sample_ptrs

    def prepare_pdf(self, runtimes):
        if self.pdf is None:
            raise ValueError("Create default(lambertian) pdf if it is not specified")
        self.pdf.prepare(runtimes)
        name = self.pdf.method_name()
        pdf_ptrs = [r.address_label(name) for r in runtimes]
        return pdf_ptrs

    def prepare_emission(self, runtimes, col_mgr):
        emission = self.emission
        if emission is None:
            code = """
shadepoint.material_emission = spectrum(0.0)
            """
            emission = SurfaceShader(code, props={}, col_mgr=col_mgr)
        emission.prepare(runtimes)
        name = emission.method_name()
        emission_ptrs = [r.address_label(name) for r in runtimes]
        return emission_ptrs

class MaterialManager:
    def __init__(self):
        self._materials = []
        self._materials_d = {}
        self._idx = {}

    def add(self, name, material):
        if name in self._materials_d:
            raise ValueError("Material allready exist!")
        if not isinstance(material, Material):
            raise ValueError("Type error. Material is expected!", material)
        self._materials.append(material)
        self._materials_d[name] = material

        idx = self._materials.index(material)
        self._idx[idx] = (name, material)

    def is_emissive(self, idx):
        m = self._idx[idx][1]
        return m.emission is not None 

    def name(self, idx):
        return self._idx[idx][0]

    def material(self, idx):
        return self._idx[idx][1]

    def remove(self, name):
        pass

    def has_material(self, name):
        return name in self._materials_d

    def index(self, name):
        if name not in self._materials_d:
            raise ValueError("Material doesn't exist!")
        m = self._materials_d[name]
        return self._materials.index(m)

    def prepare_bsdf(self, label, runtimes):
        shader = func_pointers_shader(label, runtimes,
                 self._materials, lambda m, run: m.prepare_bsdf(run))
        return shader

    def prepare_sample(self, label, runtimes):
        shader = func_pointers_shader(label, runtimes,
                 self._materials, lambda m, run: m.prepare_sample(run))
        return shader

    def prepare_pdf(self, label, runtimes):
        shader = func_pointers_shader(label, runtimes,
                 self._materials, lambda m, run: m.prepare_pdf(run))
        return shader

    def prepare_emission(self, label, runtimes, col_mgr):
        shader = func_pointers_shader(label, runtimes,
                 self._materials, lambda m, run: m.prepare_emission(run, col_mgr))
        return shader

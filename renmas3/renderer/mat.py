import platform
import collections
from ..base import Spectrum, Vec3, Float, Integer, arg_list, arg_map, Shader
from ..shapes import HitPoint
from .brdf import ShadePoint

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
    def __init__(self, brdf=None, btdf=None, bsdf=None, is_dielectric=False):
        self.brdf = brdf
        self.btdf = btdf
        self.bsdf = bsdf
        self.is_dielectric = is_dielectric

    def prepare_brdf(self, runtimes):
        self.brdf.prepare(runtimes)
        name = self.brdf.method_name()
        brdf_ptrs = [r.address_label(name) for r in runtimes]
        return brdf_ptrs

class MaterialManager:
    def __init__(self):
        self._materials = []
        self._materials_d = {}

    def add(self, name, material):
        if name in self._materials_d:
            raise ValueError("Material allready exist!")
        if not isinstance(material, Material):
            raise ValueError("Type error. Material is expected!", material)
        self._materials.append(material)
        self._materials_d[name] = material

    def remove(self, name):
        pass

    def index(self, name):
        if name not in self._materials_d:
            raise ValueError("Material doesn't exist!")
        m = self._materials_d[name]
        return self._materials.index(m)

    def prepare_brdfs(self, label, runtimes):
        shader = func_pointers_shader(label, runtimes,
                 self._materials, lambda m, run: m.prepare_brdf(run))
        return shader


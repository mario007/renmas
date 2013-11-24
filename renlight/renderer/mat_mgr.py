
import os
from renlight.sdl import Loader, Shader
from renlight.sdl.args import parse_args, StructArgPtr
from renlight.vector import Vector3
from .hitpoint import HitPoint
from .shadepoint import ShadePoint


class Material:
    def __init__(self):
        self.bsdf = None
        self.sampling = None
        self.emission = None

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'mat_shaders')
        self._loader = Loader([path])

    def _load_args(self, name):
        args = []
        props = self._loader.load(name, 'props.txt')
        if props is not None:
            args = parse_args(props)
        return args

    def _func_args(self, spectrum):
        wi = Vector3(0.0, 0.0, 0.0)
        wo = Vector3(0.0, 0.0, 0.0)
        ref = spectrum.zero()
        sh = ShadePoint(wi, wo, 0.0, ref)
        hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
        func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sh)]
        return func_args

    def load(self, shader_name, spectrum):
        self.bsdf = None
        self.sampling = None
        self.emission = None
        code = self._loader.load(shader_name, 'bsdf.py')
        #TODO hitpoint, shadepoint function arguments
        if code is not None:
            args = self._load_args(shader_name)
            name = 'bsdf_' + str(id(args))
            func_args = self._func_args(spectrum)
            self.bsdf = Shader(code=code, args=args, name=name,
                               func_args=func_args, is_func=True)

        code = self._loader.load(shader_name, 'sampling.py')
        if code is not None:
            args = self._load_args(shader_name)
            self.sampling = Shader(code=code, args=args)

        code = self._loader.load(shader_name, 'emission.py')
        if code is not None:
            args = self._load_args(shader_name)
            self.emission = Shader(code=code, args=args)

    def compile(self, shaders=[]):
        if self.bsdf is not None:
            self.bsdf.compile(shaders)
        if self.sampling is not None:
            self.sampling.compile(shaders)
        if self.emission is not None:
            self.emission.compile(shaders)

    def prepare(self, runtimes):
        if self.bsdf is not None:
            self.bsdf.prepare(runtimes)
        if self.sampling is not None:
            self.sampling.prepare(runtimes)
        if self.emission is not None:
            self.emission.prepare(runtimes)


class MaterialManager:
    def __init__(self):
        self._materials = []
        self._materials_d = {}
        self._idx = {}

    def add(self, name, material):
        if not isinstance(material, Material):
            raise ValueError("Material is expected!", name, material)
        if name in self._materials_d:
            raise ValueError("Material allready exist!", name, material)

        self._materials.append(material)
        self._materials_d[name] = material

        idx = self._materials.index(material)
        self._idx[idx] = (name, material)

    def name(self, idx):
        return self._idx[idx][0]

    def material(self, idx):
        return self._idx[idx][1]

    def index(self, name):
        if name not in self._materials_d:
            raise ValueError("Material doesn't exist!", name)
        m = self._materials_d[name]
        return self._materials.index(m)

    def has_material(self, name):
        return name in self._materials_d

    def compile(self):
        # shadepoint, hitpoint, index
        code = """
ptr = func_pointers[index]
call_indirect(hitpoint, shadepoint, ptr)
        """
        pass

    def prepare(self, runtimes):
        pass


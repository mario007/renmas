
import os.path
from tdasm import Runtime
from sdl import Loader, parse_args, Shader, ImagePRGBA, StructArg, RGBSpectrum

from sdl.arr import ObjArray, ArrayArg
from .shadepoint import ShadePoint

class Integrator:
    def __init__(self):

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'int_shaders')
        self._loader = Loader([path])

    def load(self, shader_name, sam_mgr, spectral=False):

        text = self._loader.load(shader_name, 'props.txt')
        args = []
        if text is not None:
            args = parse_args(text)
        code = self._loader.load(shader_name, 'code.py')
        if code is None:
            raise ValueError("Integrator %s code is missing!" % shader_name)

        #array of shadepoints for debuging purpose
        s = sam_mgr.zero() if spectral else RGBSpectrum(0.0, 0.0, 0.0)
        sp = ShadePoint.factory(s)
        arr = ObjArray(sp)
        for i in range(10):
            arr.append(sp)
        arg = ArrayArg('path_array', arr)

        args.append(arg)


        hdr_buffer = StructArg('hdr_buffer', ImagePRGBA(1, 1))
        args.append(hdr_buffer)
        self.shader = Shader(code=code, args=args)

    def compile(self, shaders=[]):
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

    def execute(self, hdr_buffer):
        self.shader.set_value('hdr_buffer', hdr_buffer)
        self.shader.execute()

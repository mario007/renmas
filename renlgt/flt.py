

import os.path
from tdasm import Runtime
from sdl import Loader, parse_args, StructArgPtr, Shader, FloatArg

from .sample import Sample


class SampleFilter:
    def __init__(self, xwidth=1.0, ywidth=1.0):

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'flt_shaders')
        self._loader = Loader([path])

        self.xwidth = xwidth
        self.ywidth = ywidth

    def load(self, shader_name):
        args = []
        text = self._loader.load(shader_name, 'props.txt')
        if text is not None:
            args = parse_args(text)

        args.append(FloatArg('xwidth', self.xwidth))
        args.append(FloatArg('ywidth', self.ywidth))

        code = self._loader.load(shader_name, 'code.py')
        if code is None:
            raise ValueError("code.py in %s shader dont exist!" % shader_name)

        func_args = [StructArgPtr('sample', Sample.factory())]

        self.shader = Shader(code=code, args=args, name='filter_sample',
                             func_args=func_args, is_func=True)

    def compile(self, shaders=[]):
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

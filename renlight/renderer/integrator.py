
import os
from renlight.sdl import Loader, Shader
from renlight.sdl.args import parse_args


class Integrator:
    def __init__(self):

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'int_shaders')
        self._loader = Loader([path])

    def load(self, shader_name):

        text = self._loader.load(shader_name, 'props.txt')
        args = []
        if text is not None:
            args = parse_args(text)
        code = self._loader.load(shader_name, 'code.py')
        self.shader = Shader(code=code, args=args)

    def compile(self, shaders=[]):
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

    def execute(self):
        self.shader.execute()


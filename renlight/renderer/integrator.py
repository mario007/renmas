
import os
from renlight.sdl import Loader, Shader, IntArg


class Integrator:
    def __init__(self):

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'int_shaders')
        self._loader = Loader([path])
        self.shader = None

    def load(self, shader_name):

        text = self._loader.load(shader_name, 'props.txt')
        #create args
        code = self._loader.load(shader_name, 'code.py')

        self.shader = Shader(code=code, args=[])

    def compile(self, shaders=[]):
        self._shaders = shaders
        for shader in shaders:
            shader.compile()
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        for shader in self._shaders:
            shader.prepare(runtimes)
        self.shader.prepare(runtimes)

    def execute(self):
        self.shader.execute()



import os
from renlight.vector import Vector3
from renlight.ray import Ray
from renlight.sdl import Loader, Shader, Vec3Arg, StructArgPtr, FloatArg

from .sample import Sample


class Camera:
    def __init__(self, eye, lookat, distance):
        self._eye = eye
        self._lookat = lookat
        self._up = Vector3(0.0, 1.0, 0.0)
        self._distance = float(distance)  # distance of image plane form eye
        self._compute_uvw()

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'cam_shaders')
        self._loader = Loader([path])

    def _compute_uvw(self):
        self._w = self._eye - self._lookat  # w is in oposite direction of view
        self._w.normalize()
        self._u = self._up.cross(self._w)
        self._u.normalize()
        self._v = self._w.cross(self._u)
        #singularity
        if self._eye.x == self._lookat.x and self._eye.z == self._lookat.z\
                and self._eye.y > self._lookat.y:  # looking vertically down
            self._u = Vector3(0.0, 0.0, 1.0)
            self._v = Vector3(1.0, 0.0, 0.0)
            self._w = Vector3(0.0, 1.0, 0.0)

        if self._eye.x == self._lookat.x and self._eye.z == self._lookat.z\
                and self._eye.y < self._lookat.y:  # looking vertically up
            self._u = Vector3(1.0, 0.0, 0.0)
            self._v = Vector3(0.0, 0.0, 1.0)
            self._w = Vector3(0.0, -1.0, 0.0)

    def load(self, shader_name):
        #TODO props
        props = self._loader.load(shader_name, 'props.txt')
        code = self._loader.load(shader_name, 'code.py')
        w = Vec3Arg('w', self._w)
        u = Vec3Arg('u', self._u)
        v = Vec3Arg('v', self._v)
        distance = FloatArg('distance', self._distance)
        eye = Vec3Arg('eye', self._eye)
        lookat = Vec3Arg('lookat', self._lookat)
        args = [w, u, v, distance, eye, lookat]

        origin = Vector3(0.0, 0.0, 0.0)
        direction = Vector3(0.0, 0.0, 0.0)
        ray = Ray(origin, direction)
        sample = Sample(0.0, 0.0, 0, 0, 0.0)
        func_args = [StructArgPtr('ray', ray), StructArgPtr('sample', sample)]

        self.shader = Shader(code=code, args=args, name='generate_ray',
                             func_args=func_args, is_func=True)

        codepy = self._loader.load(shader_name, 'codepy.py')
        self._py_code = compile(codepy, 'codepy.py', 'exec')

    def compile(self):
        self.shader.compile()

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

    def execute_py(self, ray, sample):
        d = {'camera': self, 'sample': sample, 'ray': ray}
        exec(self._py_code, d, d)

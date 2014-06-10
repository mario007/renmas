
import os.path
from tdasm import Runtime
from sdl import Vector3, Loader, Vec3Arg, FloatArg,\
    Ray, StructArgPtr, Shader, StructArg

from .sample import Sample
from .parse_args import parse_args


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
        self._standalone = None
        self._shader_name = None

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
        args = []
        text = self._loader.load(shader_name, 'props.txt')
        if text is not None:
            args = parse_args(text)
        w = Vec3Arg('w', self._w)
        u = Vec3Arg('u', self._u)
        v = Vec3Arg('v', self._v)
        distance = FloatArg('distance', self._distance)
        eye = Vec3Arg('eye', self._eye)
        lookat = Vec3Arg('lookat', self._lookat)
        args.extend([w, u, v, distance, eye, lookat])

        code = self._loader.load(shader_name, 'code.py')
        if code is None:
            raise ValueError("code.py in %s shader dont exist!" % shader_name)
        sample = Sample(0.0, 0.0, 0.0, 0.0, 0, 0, 0.0)
        func_args = [StructArgPtr('ray', Ray.factory()),
                     StructArgPtr('sample', sample)]
        self._shader_name = shader_name

        self.shader = Shader(code=code, args=args, name='generate_ray',
                             func_args=func_args, is_func=True)

    def compile(self, shaders=[]):
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)

    def prepare_standalone(self):

        runtimes = [Runtime()]
        self.compile()
        self.prepare(runtimes)

        code = """
ray = Ray()
generate_ray(ray, sample)
origin = ray.origin
direction = ray.direction
        """
        origin = Vec3Arg('origin', Vector3(0.0, 0.0, 0.0))
        direction = Vec3Arg('direction', Vector3(0.0, 0.0, 0.0))
        sample = Sample(0.0, 0.0, 0.0, 0.0, 0, 0, 0.0)
        sample_arg = StructArg('sample', sample)
        args = [origin, direction, sample_arg]
        self._standalone = shader = Shader(code=code, args=args)

        shader.compile([self.shader])
        shader.prepare(runtimes)

    def generate_ray(self, sample):

        self._standalone.set_value('sample', sample)
        self._standalone.execute()
        origin = self._standalone.get_value('origin')
        direction = self._standalone.get_value('direction')
        ray = Ray(origin, direction)
        return ray

    def output(self):
        type_name = 'Unknown' if self._shader_name is None else self._shader_name
        txt = 'Camera\n'
        txt += 'type = %s\n' % type_name
        txt += 'eye = %f, %f, %f\n' % (self._eye.x, self._eye.y, self._eye.z)
        txt += 'lookat = %f, %f, %f\n' % (self._lookat.x, self._lookat.y, self._lookat.z)
        txt += 'distance = %f\n' % self._distance
        txt += 'End\n'
        return txt

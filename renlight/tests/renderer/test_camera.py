
import unittest

from tdasm import Runtime

from renlight.vector import Vector3
from renlight.ray import Ray
from renlight.renderer.camera import Camera
from renlight.sdl.shader import Shader
from renlight.sdl import Vec3Arg
from renlight.renderer.sample import Sample


class CameraTest(unittest.TestCase):

    def test_cameras(self):
        eye = Vector3(0.0, 10.0, 5.0)
        lookat = Vector3(0.0, 0.0, 0.0)
        distance = 100.0

        cam = Camera(eye, lookat, distance)
        cam.load('pinhole')
        cam.compile()
        runtimes = [Runtime()]
        cam.prepare(runtimes)

        code = """
ray = Ray()
sample = Sample()
sample.x = 2.2
sample.y = 2.5
generate_ray(ray, sample)
origin = ray.origin
direction = ray.direction
        """
        origin = Vec3Arg('origin', Vector3(0.0, 0.0, 0.0))
        direction = Vec3Arg('direction', Vector3(0.0, 0.0, 0.0))
        args = [origin, direction]
        shader = Shader(code=code, args=args)
        shader.compile([cam.shader])
        shader.prepare(runtimes)
        shader.execute()

        ray = Ray(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))
        sample = Sample(2.2, 2.5, 2, 2, 1.0)
        cam.execute_py(ray, sample)

        v = shader.get_value('origin')
        o = ray.origin
        self.assertAlmostEqual(v.x, o.x)
        self.assertAlmostEqual(v.y, o.y)
        self.assertAlmostEqual(v.z, o.z)

        v = shader.get_value('direction')
        d = ray.direction
        self.assertAlmostEqual(v.x, d.x)
        self.assertAlmostEqual(v.y, d.y)
        self.assertAlmostEqual(v.z, d.z)

if __name__ == "__main__":
    unittest.main()

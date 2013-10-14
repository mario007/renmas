
import unittest

from tdasm import Runtime

from renlight.vector import Vector3
from renlight.ray import Ray
from renlight.sdl.shader import Shader
from renlight.sdl import StructArg, IntArg
from renlight.renderer.hitpoint import HitPoint
from renlight.renderer.sphere import Sphere


class SphereTest(unittest.TestCase):

    def test_isect_b_sph(self):
        sph_shader = Sphere.isect_b_shader()
        sph_shader.compile()
        runtimes = [Runtime()]
        sph_shader.prepare(runtimes)

        code = """
min_dist = 99999.0
p1 = isect_b_sphere(ray, sphere, min_dist)
        """

        direction = Vector3(-1.0, -1.0, -1.0)
        direction.normalize()
        ray = Ray(Vector3(5.0, 5.0, 5.0), direction)
        sphere = Sphere(Vector3(0.0, 0.0, 0.0), 2.0, 0)

        r_arg = StructArg('ray', ray)
        sph_arg = StructArg('sphere', sphere)
        p1 = IntArg('p1', 6)

        args = [r_arg, sph_arg, p1]
        shader = Shader(code=code, args=args)
        shader.compile([sph_shader])

        shader.prepare(runtimes)
        shader.execute()

        result = shader.get_value('p1')
        self.assertEqual(result, 1)

    def test_isect_sph(self):
        sph_shader = Sphere.isect_shader()
        sph_shader.compile()
        runtimes = [Runtime()]
        sph_shader.prepare(runtimes)

        code = """
min_dist = 99999.0
p1 = isect_sphere(ray, sphere, hitpoint, min_dist)
        """

        direction = Vector3(-1.0, -1.0, -1.0)
        direction.normalize()
        ray = Ray(Vector3(5.0, 5.0, 5.0), direction)
        sphere = Sphere(Vector3(0.0, 0.0, 0.0), 2.0, 0)
        hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                            Vector3(0.0, 0.0, 0.0), 6, 0.0, 0.0)

        r_arg = StructArg('ray', ray)
        sph_arg = StructArg('sphere', sphere)
        harg = StructArg('hitpoint', hitpoint)
        p1 = IntArg('p1', 6)

        args = [r_arg, sph_arg, harg, p1]
        shader = Shader(code=code, args=args)
        shader.compile([sph_shader])

        shader.prepare(runtimes)
        shader.execute()

        hp2 = sphere.isect(ray)
        hitpoint = shader.get_value('hitpoint')
        self.assertAlmostEqual(hp2.t, hitpoint.t)
        self.assertEqual(hp2.mat_idx, hitpoint.mat_idx)
        n1 = hp2.normal
        n2 = hitpoint.normal
        self.assertAlmostEqual(n1.x, n2.x)
        self.assertAlmostEqual(n1.y, n2.y)
        self.assertAlmostEqual(n1.z, n2.z)
        self.assertAlmostEqual(hitpoint.hit.x, hp2.hit.x)
        self.assertAlmostEqual(hitpoint.hit.y, hp2.hit.y)
        self.assertAlmostEqual(hitpoint.hit.z, hp2.hit.z)

        result = shader.get_value('p1')
        self.assertEqual(result, 1)

if __name__ == "__main__":
    unittest.main()

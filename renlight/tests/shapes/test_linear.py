
import unittest
from tdasm import Runtime
from renlight.sdl.shader import Shader
from renlight.sdl.args import StructArg, IntArg

from renlight.ray import Ray
from renlight.vector import Vector3
from renlight.renderer.sphere import Sphere
from renlight.renderer.hitpoint import HitPoint
from renlight.renderer.shp_mgr import ShapeManager
from renlight.renderer.linear import LinearIsect


class LinearIsectTests(unittest.TestCase):
    def test_linear(self):
        sphere = Sphere(Vector3(0.0, 0.0, 0.0), 2.0, 0)
        mgr = ShapeManager()
        mgr.add('sph1', sphere)
        sphere2 = Sphere(Vector3(0.0, 2.0, 0.0), 3.0, 0)
        mgr.add('sph2', sphere2)

        isector = LinearIsect(mgr)
        runtimes = [Runtime()]

        direction = Vector3(-1.0, -1.0, -1.0)
        direction.normalize()
        ray = Ray(Vector3(5.0, 5.0, 5.0), direction)

        isect_sph = Sphere.isect_shader()
        isect_sph.compile()
        isect_sph.prepare(runtimes)

        isect_shader = isector.isect_shader()
        isect_shader.compile([isect_sph])
        isect_shader.prepare(runtimes)

        code = """
min_dist = 99999.0
p1 = isect_scene(ray, hitpoint, min_dist)
        """
        direction = Vector3(-1.0, -1.0, -1.0)
        direction.normalize()
        ray = Ray(Vector3(5.0, 5.0, 5.0), direction)
        hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                            Vector3(0.0, 0.0, 0.0), 6, 0.0, 0.0)

        r_arg = StructArg('ray', ray)
        harg = StructArg('hitpoint', hitpoint)
        p1 = IntArg('p1', 6)

        args = [r_arg, harg, p1]
        shader = Shader(code=code, args=args)
        shader.compile([isect_shader])
        shader.prepare(runtimes)

        hp2 = isector.isect(ray)
        shader.execute()

        hitpoint = shader.get_value('hitpoint')

        self.assertAlmostEqual(hp2.t, hitpoint.t, places=5)
        self.assertEqual(hp2.mat_idx, hitpoint.mat_idx)
        n1 = hp2.normal
        n2 = hitpoint.normal
        self.assertAlmostEqual(n1.x, n2.x)
        self.assertAlmostEqual(n1.y, n2.y, places=6)
        self.assertAlmostEqual(n1.z, n2.z)
        self.assertAlmostEqual(hitpoint.hit.x, hp2.hit.x, places=6)
        self.assertAlmostEqual(hitpoint.hit.y, hp2.hit.y, places=6)
        self.assertAlmostEqual(hitpoint.hit.z, hp2.hit.z, places=6)

        result = shader.get_value('p1')
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()

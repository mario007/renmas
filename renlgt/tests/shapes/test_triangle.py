
import unittest

from tdasm import Runtime
from sdl import Vector3, Ray, Shader, StructArg, IntArg
from renlgt.hitpoint import HitPoint
from renlgt.triangle import FlatTriangle


class FlatTriangleTest(unittest.TestCase):

    def _almost_equal_vec3(self, v1, v2, places=7):
        self.assertAlmostEqual(v1.x, v2.x, places)
        self.assertAlmostEqual(v1.y, v2.y, places)
        self.assertAlmostEqual(v1.z, v2.z, places)


    def test_isect_flat_triangle(self):
        runtimes = [Runtime()]

        tri_shader = FlatTriangle.isect_shader('isect_flat_triangle')
        tri_shader.compile()
        tri_shader.prepare(runtimes)

        p0 = Vector3(2.2, 4.4, 6.6)
        p1 = Vector3(1.1, 1.1, 1.1)
        p2 = Vector3(5.1, -1.1, 5.1)

        origin = Vector3(0.0, 0.0, 0.0)
        direction = Vector3(3, 3.0, 3.01)
        direction.normalize()
        ray = Ray(origin, direction)
        hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                            Vector3(0.0, 0.0, 0.0), 6, 0.0, 0.0)

        t = FlatTriangle(p0, p1, p2)

        code = """
min_dist = 150.0
ret = isect_flat_triangle(ray, triangle, hitpoint, min_dist)
        """

        r_arg = StructArg('ray', ray)
        tri_arg = StructArg('triangle', t)
        harg = StructArg('hitpoint', hitpoint)
        ret = IntArg('ret', 6)

        args = [r_arg, tri_arg, harg, ret]
        shader = Shader(code=code, args=args)
        shader.compile([tri_shader.shader])
        shader.prepare(runtimes)

        shader.execute()

        min_dist = 150.0
        hit = t.isect(ray, min_dist)


        hp = shader.get_value('hitpoint')

        self.assertAlmostEqual(hit.t, hp.t, places=6)
        self._almost_equal_vec3(hit.hit, hp.hit, places=6)
        self._almost_equal_vec3(hit.normal, hp.normal, places=6)
        self.assertEqual(hit.mat_idx, hp.mat_idx)
        self.assertAlmostEqual(hit.u, hp.u)
        self.assertAlmostEqual(hit.v, hp.v)

    def test_isect_b_flat_triangle(self):
        runtimes = [Runtime()]

        tri_shader = FlatTriangle.isect_b_shader('isect_b_flat_triangle')
        tri_shader.compile()
        tri_shader.prepare(runtimes)

        p0 = Vector3(2.2, 4.4, 6.6)
        p1 = Vector3(1.1, 1.1, 1.1)
        p2 = Vector3(5.1, -1.1, 5.1)

        origin = Vector3(0.0, 0.0, 0.0)
        direction = Vector3(3, 3.0, 3.01)
        direction.normalize()
        ray = Ray(origin, direction)
        t = FlatTriangle(p0, p1, p2)

        code = """
min_dist = 150.0
ret = isect_b_flat_triangle(ray, triangle, min_dist)
        """

        r_arg = StructArg('ray', ray)
        tri_arg = StructArg('triangle', t)
        ret = IntArg('ret', 6)

        args = [r_arg, tri_arg, ret]
        shader = Shader(code=code, args=args)
        shader.compile([tri_shader.shader])
        shader.prepare(runtimes)

        shader.execute()

        min_dist = 150.0
        hit = t.isect_b(ray, min_dist)

        hit2 = shader.get_value('ret')
        if hit2 == 0:
            hit2 = False
        elif hit2 == 1:
            hit2 = True
        else:
            raise ValueError("Unexpected value for isect flat triangle ", hit2)

        self.assertEqual(hit, hit2)
            


if __name__ == "__main__":
    unittest.main()

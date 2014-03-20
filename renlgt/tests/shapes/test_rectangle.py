
import unittest

from tdasm import Runtime
from sdl import Vector3, Ray, Shader, StructArg, IntArg
from renlgt.hitpoint import HitPoint
from renlgt.rectangle import Rectangle


class RectangleTest(unittest.TestCase):

    def test_isect_rect(self):
        rect_shader = Rectangle.isect_shader('isect_rectangle')
        rect_shader.compile()
        runtimes = [Runtime()]
        rect_shader.prepare(runtimes)

        code = """
min_dist = 99999.0
p1 = isect_rectangle(ray, rectangle, hitpoint, min_dist)
        """

        origin = Vector3(3.0, 2.5, 0.0)
        direction = Vector3(0.0, 0.1, 0.88)
        direction.normalize()
        ray = Ray(origin, direction)

        point = Vector3(0.0, 0.0, 55.92)
        e1 = Vector3(55.28, 0.0, 0.0)
        e2 = Vector3(0.0, 54.88, 0.0)
        normal = Vector3(0.0, 0.0, -1.0)
        rectangle = Rectangle(point, e1, e2, normal)

        hitpoint = HitPoint.factory()
        hitpoint.mat_idx = 5

        r_arg = StructArg('ray', ray)
        sph_arg = StructArg('rectangle', rectangle)
        harg = StructArg('hitpoint', hitpoint)
        p1 = IntArg('p1', 6)

        args = [r_arg, sph_arg, harg, p1]
        shader = Shader(code=code, args=args)
        shader.compile([rect_shader.shader])
        shader.prepare(runtimes)

        shader.execute()
        hp2 = rectangle.isect(ray)

        hitpoint = shader.get_value('hitpoint')
        self.assertAlmostEqual(hp2.t, hitpoint.t, places=5)
        self.assertEqual(hp2.mat_idx, hitpoint.mat_idx)
        n1 = hp2.normal
        n2 = hitpoint.normal
        self.assertAlmostEqual(n1.x, n2.x)
        self.assertAlmostEqual(n1.y, n2.y)
        self.assertAlmostEqual(n1.z, n2.z)
        self.assertAlmostEqual(hitpoint.hit.x, hp2.hit.x, places=5)
        self.assertAlmostEqual(hitpoint.hit.y, hp2.hit.y, places=5)
        self.assertAlmostEqual(hitpoint.hit.z, hp2.hit.z, places=5)

        result = shader.get_value('p1')
        self.assertEqual(result, 1)

    def test_isect_b_rect(self):
        rect_shader = Rectangle.isect_b_shader('isect_b_rectangle')
        rect_shader.compile()
        runtimes = [Runtime()]
        rect_shader.prepare(runtimes)

        code = """
min_dist = 99999.0
p1 = isect_b_rectangle(ray, rectangle, min_dist)
        """

        origin = Vector3(3.0, 2.5, 0.0)
        direction = Vector3(0.0, 0.1, 0.88)
        direction.normalize()
        ray = Ray(origin, direction)

        point = Vector3(0.0, 0.0, 55.92)
        e1 = Vector3(55.28, 0.0, 0.0)
        e2 = Vector3(0.0, 54.88, 0.0)
        normal = Vector3(0.0, 0.0, -1.0)
        rectangle = Rectangle(point, e1, e2, normal)

        r_arg = StructArg('ray', ray)
        sph_arg = StructArg('rectangle', rectangle)
        p1 = IntArg('p1', 6)

        args = [r_arg, sph_arg, p1]
        shader = Shader(code=code, args=args)
        shader.compile([rect_shader.shader])

        shader.prepare(runtimes)
        shader.execute()

        result = shader.get_value('p1')
        self.assertEqual(result, 1)

if __name__ == "__main__":
    unittest.main()

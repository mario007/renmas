
import unittest
from tdasm import Runtime
from sdl import Shader, StructArg, IntArg, Ray, Vector3

from renlgt.sphere import Sphere
from renlgt.hitpoint import HitPoint
from renlgt.shp_mgr import ShapeManager
from renlgt.linear import LinearIsect


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

        isector.compile()
        isector.prepare(runtimes)

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
        shader.compile([isector.shader])
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

    def test_linear_visiblity(self):
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

        isector.compile()
        isector.prepare(runtimes)

        code = """
p1 = (9, 8, 7)
p2 = (-2, -5, -3)
ret = visibility(p1, p2)
        """
        ret = IntArg('ret', 6)
        args = [ret]
        shader = Shader(code=code, args=args)
        shader.compile([isector.visible_shader])
        shader.prepare(runtimes)

        p1 = Vector3(9.0, 8.0, 7.0)
        p2 = Vector3(-2.0, -5.0, -3.0)
        ret = isector.visibility(p1, p2)
        shader.execute()
        ret_s = shader.get_value('ret')
        if ret is True and ret_s == 0:
            raise ValueError("Linear visiblity is calculated wrong", ret, ret_s)
        if ret is False and ret_s == 1:
            raise ValueError("Linear visiblity is calculated wrong", ret, ret_s)


if __name__ == "__main__":
    unittest.main()

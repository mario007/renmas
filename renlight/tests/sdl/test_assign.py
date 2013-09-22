import unittest
from tdasm import Runtime
from renlight.vector import Vector2, Vector3, Vector4
from renlight.sdl.shader import Shader
from renlight.sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg


class AssignTest(unittest.TestCase):
    def test_assign(self):
        code = """
k = 55
p1 = k
m = (4, 7)
p2 = m
h = (3.13, 8, 9)
p3 = h
t = (6.6, 2.2, 9, 1)
p4 = t
r = 3.3
p5 = r
        """
        p1 = IntArg('p1', 33)
        p2 = Vec2Arg('p2', Vector2(9, 22))
        p3 = Vec3Arg('p3', Vector3(1, 4.4, 29))
        p4 = Vec4Arg('p4', Vector4(2, 3, 1.1, 2))
        p5 = FloatArg('p5', 87.33)
        shader = Shader(code=code, args=[p1, p2, p3, p4, p5])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        self.assertEqual(shader.get_value('p1'), 55)
        v = shader.get_value('p2')
        self.assertAlmostEqual(v.x, 4.0)
        self.assertAlmostEqual(v.y, 7.0)
        v = shader.get_value('p3')
        self.assertAlmostEqual(v.x, 3.13, places=6)
        self.assertAlmostEqual(v.y, 8.0)
        self.assertAlmostEqual(v.z, 9.0)
        v = shader.get_value('p4')
        self.assertAlmostEqual(v.x, 6.6, places=6)
        self.assertAlmostEqual(v.y, 2.2)
        self.assertAlmostEqual(v.z, 9.0)
        self.assertAlmostEqual(v.w, 1.0)
        v = shader.get_value('p5')
        self.assertAlmostEqual(v, 3.3)

if __name__ == "__main__":
    unittest.main()

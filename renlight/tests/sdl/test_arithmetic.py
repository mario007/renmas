
import unittest
from tdasm import Runtime
from renlight.vector import Vector2, Vector3, Vector4
from renlight.sdl.shader import Shader
from renlight.sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg


class ArithmeticTests(unittest.TestCase):

    def test_arithmetic(self):
        code = """
a1 = 33
a2 = 22
p1 = a1 + a2
a1 = 22.3
a2 = 11.1
p2 = a1 + a2
a1 = 44
a2 = -2.36
p3 = a1 * a2
a1 = (2.3, 4)
a2 = 5
p4 = a1 * a2

a1 = (3, 4, 6.6)
a2 = (7, 4.3, 2.6)
p5 = a1 - a2

a1 = (1, 4.1, 5.5, 9.9)
a2 = (0.22, 3.3, 2.6, 6.6)
p6 = a1 / a2
        """
        p1 = IntArg('p1', 33)
        p2 = FloatArg('p2', 55.5)
        p3 = FloatArg('p3', 55.5)
        p4 = Vec2Arg('p4', Vector2(0.0, 0.0))
        p5 = Vec3Arg('p5', Vector3(0.0, 0.0, 0.0))
        p6 = Vec4Arg('p6', Vector4(0.0, 0.0, 0.0, 0.0))

        shader = Shader(code=code, args=[p1, p2, p3, p4, p5, p6])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        rez = shader.get_value('p1')
        self.assertEqual(rez, 33 + 22)
        rez = shader.get_value('p2')
        self.assertAlmostEqual(rez, 22.3 + 11.1, places=5)
        rez = shader.get_value('p3')
        self.assertAlmostEqual(rez, 44 * -2.36, places=5)
        rez = shader.get_value('p4')
        self.assertAlmostEqual(rez.x, 5 * 2.3, places=5)
        self.assertAlmostEqual(rez.y, 5 * 4, places=5)
        rez = shader.get_value('p5')
        self.assertAlmostEqual(rez.x, 3 - 7.0, places=5)
        self.assertAlmostEqual(rez.y, 4 - 4.3, places=5)
        self.assertAlmostEqual(rez.z, 6.6 - 2.6, places=5)
        rez = shader.get_value('p6')
        self.assertAlmostEqual(rez.x, 1 / 0.22, places=5)
        self.assertAlmostEqual(rez.y, 4.1 / 3.3, places=5)
        self.assertAlmostEqual(rez.z, 5.5 / 2.6, places=5)
        self.assertAlmostEqual(rez.w, 9.9 / 6.6, places=5)

    def test_expr(self):
        code = """
        """
        shader = Shader(code=code, args=[])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

if __name__ == "__main__":
    unittest.main()


import unittest
from tdasm import Runtime
from sdl.vector import Vector2, Vector3, Vector4
from sdl.shader import Shader
from sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg, StructArgPtr
from sdl.args import register_struct


class ConditionsTests(unittest.TestCase):

    def test_con(self):
        code = """
a = 33
if a:
    p1 = 22

b = 22
if b > 15:
    p2 = 1.1

tmp = 4.4
tmp2 = 1.2
if tmp > tmp2:
    p3 = 2.2

tmp = 5.5
if tmp2 < tmp:
    p4 = 1.5

        """

        p1 = IntArg('p1', 55)
        p2 = FloatArg('p2', 4.4)
        p3 = FloatArg('p3', 9.4)
        p4 = FloatArg('p4', 2.4)

        shader = Shader(code=code, args=[p1, p2, p3, p4])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertEqual(p, 22)
        p = shader.get_value('p2')
        self.assertAlmostEqual(p, 1.1)
        p = shader.get_value('p3')
        self.assertAlmostEqual(p, 2.2)
        p = shader.get_value('p4')
        self.assertAlmostEqual(p, 1.5)

if __name__ == "__main__":
    unittest.main()


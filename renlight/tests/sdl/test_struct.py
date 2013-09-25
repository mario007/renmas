
import unittest
from tdasm import Runtime
from renlight.vector import Vector2, Vector3, Vector4
from renlight.sdl.shader import Shader
from renlight.sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg
from renlight.sdl.args import register_struct


class MyPoint:
    def __init__(self, x, y, k, m, p):
        self.x = x
        self.y = y
        self.k = k
        self.m = m
        self.p = p

register_struct(MyPoint, 'MyPoint', fields=[('x', IntArg),
               ('y', FloatArg), ('k', Vec2Arg), ('m', Vec3Arg),
               ('p', Vec4Arg)], factory=lambda:
               MyPoint(1, 2.0, Vector2(2.2, 3.3), Vector3(3.3, 5.5, 7.7), Vector4(3.3, 6.6, 8.8, 9.9)))


class StructTests(unittest.TestCase):

    def test_struct(self):
        code = """
a1 = MyPoint()
tmp = 66
a1.x = tmp
p1 = a1.x

tmp = 4.4
a1.y = tmp
p2 = a1.y

tmp = (6, 7)
a1.k = tmp
p3 = a1.k

tmp = (3, 4, 6)
a1.m = tmp
p4 = a1.m

tmp = (2, 4, 6, 7)
a1.p = tmp
p5 = a1.p

        """
        #p1 = IntArg('p1', 44) #TODO implicit conversion int to float
        p1 = IntArg('p1', 44)
        p2 = FloatArg('p2', 2.2)
        p3 = Vec2Arg('p3', Vector2(5.5, 7.7))
        p4 = Vec3Arg('p4', Vector3(2.2, 2.2, 4.4))
        p5 = Vec4Arg('p5', Vector4(8.8, 5.5, 3.3, 1.1))
        shader = Shader(code=code, args=[p1, p2, p3, p4, p5])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        v = shader.get_value('p1')
        self.assertEqual(v, 66)
        v = shader.get_value('p2')
        self.assertAlmostEqual(v, 4.4, places=6)
        v = shader.get_value('p3')
        self.assertAlmostEqual(v.x, 6.0, places=6)
        self.assertAlmostEqual(v.y, 7.0, places=6)
        v = shader.get_value('p4')
        self.assertAlmostEqual(v.x, 3.0, places=6)
        self.assertAlmostEqual(v.y, 4.0, places=6)
        self.assertAlmostEqual(v.z, 6.0, places=6)
        v = shader.get_value('p5')
        self.assertAlmostEqual(v.x, 2.0, places=6)
        self.assertAlmostEqual(v.y, 4.0, places=6)
        self.assertAlmostEqual(v.z, 6.0, places=6)
        self.assertAlmostEqual(v.w, 7.0, places=6)

if __name__ == "__main__":
    unittest.main()


import unittest
from tdasm import Runtime
from sdl.vector import Vector2, Vector3, Vector4
from sdl.shader import Shader
from sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg, StructArgPtr
from sdl.args import register_struct


class TestPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

register_struct(TestPoint, 'TestPoint', fields=[('x', FloatArg),
               ('y', FloatArg)], factory=lambda: TestPoint(1.0, 2.0))


class FuncCallTests(unittest.TestCase):

    def setUp(self):
        self.runtimes = [Runtime()]

    def test_call(self):
        code = """
tmp = p1 + p2 + p3
p4.x = 55.99
return tmp
        """
        p1 = FloatArg('p1', 2.0)
        p2 = IntArg('p2', 0)
        p3 = FloatArg('p3', 0.0)
        p4 = StructArgPtr('p4', TestPoint(4.4, 5.5))
        shader = Shader(code=code, args=[], name='adding',
                        func_args=[p1, p2, p3, p4], is_func=True)
        shader.compile()
        shader.prepare(self.runtimes)

        code2 = """
p1 = 44
p2 = 7
point = TestPoint()
rez = adding(55.4, p1, p2, point)
rez2 = point.x
        """
        rez = FloatArg('rez', 11.33)
        rez2 = FloatArg('rez2', 1.0)
        shader2 = Shader(code=code2, args=[rez, rez2])
        shader2.compile([shader])
        shader2.prepare(self.runtimes)
        shader2.execute()

        rez = shader2.get_value('rez')
        rez2 = shader2.get_value('rez2')
        self.assertAlmostEqual(rez, 55.4 + 44 + 7, places=5)
        self.assertAlmostEqual(rez2, 55.99, places=5)

if __name__ == "__main__":
    unittest.main()

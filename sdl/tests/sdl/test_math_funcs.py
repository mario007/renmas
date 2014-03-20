
import unittest
from math import log, exp, acos, asin, atan, atan2, cos, sin, tan
from tdasm import Runtime
from sdl.vector import Vector3
from sdl.shader import Shader
from sdl.args import FloatArg, Vec3Arg


class MathFuncsTest(unittest.TestCase):
    def test_log(self):
        code = """
val = 4.4
t1 = log(val)
val = (4.6, 6.6, 9.9)
t2 = log(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, log(4.4), places=5)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, log(4.6), places=4)
        self.assertAlmostEqual(v.y, log(6.6), places=4)
        self.assertAlmostEqual(v.z, log(9.9), places=4)

    def test_exp(self):
        code = """
val = 4.4
t1 = exp(val)
val = (4.6, 1.6, 2.9)
t2 = exp(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, exp(4.4), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, exp(4.6), places=2)
        self.assertAlmostEqual(v.y, exp(1.6), places=3)
        self.assertAlmostEqual(v.z, exp(2.9), places=3)

    def test_pow(self):
        code = """
val1 = 1.4
val2 = 1.2
t1 = pow(val1, val2)
val1 = (1.6, 1.3, 2.2)
val2 = (1.1, 1.2, 1.3)
t2 = pow(val1, val2)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, pow(1.4, 1.2), places=3)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, pow(1.6, 1.1), places=3)
        self.assertAlmostEqual(v.y, pow(1.3, 1.2), places=3)
        self.assertAlmostEqual(v.z, pow(2.2, 1.3), places=3)

    def test_atanr2(self):
        code = """
val1 = 1.4
val2 = 1.2
t1 = atanr2(val1, val2)
val1 = (1.6, 1.3, 2.2)
val2 = (1.1, 1.2, 1.3)
t2 = atanr2(val1, val2)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, atan2(1.4, 1.0 / 1.2), places=3)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, atan2(1.6, 1.0 / 1.1), places=3)
        self.assertAlmostEqual(v.y, atan2(1.3, 1.0 / 1.2), places=3)
        self.assertAlmostEqual(v.z, atan2(2.2, 1.0 / 1.3), places=3)

    def test_acos(self):
        code = """
val = 0.5
t1 = acos(val)
val = (0.6, 0.3, -0.3)
t2 = acos(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, acos(0.5), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, acos(0.6), places=2)
        self.assertAlmostEqual(v.y, acos(0.3), places=3)
        self.assertAlmostEqual(v.z, acos(-0.3), places=3)

    def test_asin(self):
        code = """
val = 0.5
t1 = asin(val)
val = (0.6, 0.3, -0.3)
t2 = asin(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, asin(0.5), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, asin(0.6), places=2)
        self.assertAlmostEqual(v.y, asin(0.3), places=3)
        self.assertAlmostEqual(v.z, asin(-0.3), places=3)

    def test_atan(self):
        code = """
val = 0.5
t1 = atan(val)
val = (0.6, 0.3, -0.3)
t2 = atan(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, atan(0.5), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, atan(0.6), places=2)
        self.assertAlmostEqual(v.y, atan(0.3), places=3)
        self.assertAlmostEqual(v.z, atan(-0.3), places=3)

    def test_cos(self):
        code = """
val = 0.5
t1 = cos(val)
val = (0.6, 0.3, -0.3)
t2 = cos(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, cos(0.5), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, cos(0.6), places=2)
        self.assertAlmostEqual(v.y, cos(0.3), places=3)
        self.assertAlmostEqual(v.z, cos(-0.3), places=3)

    def test_sin(self):
        code = """
val = 0.5
t1 = sin(val)
val = (0.6, 0.3, -0.3)
t2 = sin(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, sin(0.5), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, sin(0.6), places=2)
        self.assertAlmostEqual(v.y, sin(0.3), places=3)
        self.assertAlmostEqual(v.z, sin(-0.3), places=3)

    def test_tan(self):
        code = """
val = 0.5
t1 = tan(val)
val = (0.6, 0.3, -0.3)
t2 = tan(val)

        """
        t1 = FloatArg('t1', 0.0)
        t2 = Vec3Arg('t2', Vector3(1, 4.4, 29))
        shader = Shader(code=code, args=[t1, t2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        v = shader.get_value('t1')
        self.assertAlmostEqual(v, tan(0.5), places=2)
        v = shader.get_value('t2')
        self.assertAlmostEqual(v.x, tan(0.6), places=2)
        self.assertAlmostEqual(v.y, tan(0.3), places=3)
        self.assertAlmostEqual(v.z, tan(-0.3), places=3)

if __name__ == "__main__":
    unittest.main()

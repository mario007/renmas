
import unittest
from math import log, exp
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

if __name__ == "__main__":
    unittest.main()

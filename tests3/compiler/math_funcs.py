import math
import unittest
from random import random

from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class MathTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_pow(self):
        code = """
ret = pow(1.4, 4.4)
ret2 = pow((1.1, 1.25), (2.1, 3.1))
ret3 = pow((1.3, 1.7, 1.8), (1.11, 2.11, 1.45))
ret4 = pow((1.9, 1.15, 2.11, 2.22), (1.77, 2.21, 2.5, 2.71))
        """
        props = {'ret':1.1, 'ret2':Vector2(2.2, 4), 'ret3':Vector3(5,6,7),
                'ret4':Vector4(11,1,1,1)}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val, pow(1.4, 4.4), places=3)
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val.x, pow(1.1, 2.1), places=3)
        self.assertAlmostEqual(val.y, pow(1.25, 3.1), places=3)
        val = bs.shader.get_value('ret3')
        self.assertAlmostEqual(val.x, pow(1.3, 1.11), places=3)
        self.assertAlmostEqual(val.y, pow(1.7, 2.11), places=3)
        self.assertAlmostEqual(val.z, pow(1.8, 1.45), places=3)
        val = bs.shader.get_value('ret4')
        self.assertAlmostEqual(val.x, pow(1.9, 1.77), places=3)
        self.assertAlmostEqual(val.y, pow(1.15, 2.21), places=3)
        self.assertAlmostEqual(val.z, pow(2.11, 2.5), places=3)
        self.assertAlmostEqual(val.w, pow(2.22, 2.71), places=3)

    def math_fun_test(self, fun, py_fun):
        num = random()
        nums = (random(), random())

        line1 = "ret = %s(%f)\n" % (fun, num)
        line2 = "ret2 = %s((%f, %f))\n" % (fun, nums[0], nums[1])
        code = line1 + line2

        props = {'ret':1.1, 'ret2':Vector2(2.2, 4), 'ret3':Vector3(5,6,7),
                'ret4':Vector4(11,1,1,1)}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val, py_fun(num), places=3)
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val.x, py_fun(nums[0]), places=3)
        self.assertAlmostEqual(val.y, py_fun(nums[1]), places=3)

    def test_log(self):
        self.math_fun_test('log', math.log)

    def test_exp(self):
        self.math_fun_test('exp', math.exp)

    def test_sin(self):
        self.math_fun_test('sin', math.sin)

    def test_cos(self):
        self.math_fun_test('cos', math.cos)

    def test_sqrt(self):
        self.math_fun_test('sqrt', math.sqrt)

    def test_acos(self):
        self.math_fun_test('acos', math.acos)

    def test_asin(self):
        self.math_fun_test('asin', math.asin)

    def test_tan(self):
        self.math_fun_test('tan', math.tan)

    def test_atan(self):
        self.math_fun_test('atan', math.atan)

    def test_atanr2(self):
        code = """
ret = atanr2(1.4, 4.4)
ret2 = atanr2((1.1, 1.25), (2.1, 3.1))
        """
        props = {'ret':1.1, 'ret2':Vector2(2.2, 4), 'ret3':Vector3(5,6,7),
                'ret4':Vector4(11,1,1,1)}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val, math.atan2(1.4, 1.0/4.4), places=3)
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val.x, math.atan2(1.1, 1.0/2.1), places=3)
        self.assertAlmostEqual(val.y, math.atan2(1.25, 1.0/3.1), places=3)

if __name__ == "__main__":
    unittest.main()



import unittest
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

    def test_log(self):
        code = """
ret = log(1.4)
        """
        props = {'ret':1.1, 'ret2':Vector2(2.2, 4), 'ret3':Vector3(5,6,7),
                'ret4':Vector4(11,1,1,1)}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        print (val)
        import math
        print (math.log(1.4))

if __name__ == "__main__":
    unittest.main()


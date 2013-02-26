
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class Arith1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
r1 = a1 + a2
r2 = a1 * a2 
r3 = a4 * (0.5, 0.5)
r4 = a5 / (0.5, 0.5, 0.5)
r5 = (7,7,7,7) + a6 
r6 = a3 / 3
r7 = a7 % 18
        """
        props = {'a1':1.1, 'a2':2.2, 'r1':1.1, 'r2':3.3,
                'a3':55, 'a4':Vector2(2.2, 4), 'a5':Vector3(5,6,7),
                'a6':Vector4(3,4,5,6), 'r3':Vector2(3,4), 'r4':Vector3(1,1,1),
                'r5':Vector4(11,1,1,1), 'r6':88, 'a7':789, 'r7':1}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('r1')
        self.assertAlmostEqual(val, 2.2 + 1.1, places=5)
        val = bs.shader.get_value('r2')
        self.assertAlmostEqual(val, 1.1 * 2.2, places=5)
        val = bs.shader.get_value('r3')
        self.assertAlmostEqual(val.x, 2.2*0.5, places=5)
        self.assertAlmostEqual(val.y, 4.0*0.5, places=5)
        val = bs.shader.get_value('r4')
        self.assertAlmostEqual(val.x, 5*2.0, places=5)
        self.assertAlmostEqual(val.y, 6*2.0, places=5)
        self.assertAlmostEqual(val.z, 7*2.0, places=5)
        val = bs.shader.get_value('r5')
        self.assertAlmostEqual(val.x, 7+3.0, places=5)
        self.assertAlmostEqual(val.y, 7+4.0, places=5)
        self.assertAlmostEqual(val.z, 7+5.0, places=5)
        self.assertAlmostEqual(val.w, 7+6.0, places=5)
        val = bs.shader.get_value('r6')
        self.assertEqual(val, 55//3)
        val = bs.shader.get_value('r7')
        self.assertEqual(val, 789 % 18)

    def test_arith2(self):

        code = """
r1 = a1 + 5
r2 = 4 * a2

r3 = 8 * a4
r4 = a5 * 1.1

r5 = a6 * 0.5

        """
        props = {'a1':1.1, 'a2':2.2, 'r1':1.1, 'r2':3.3,
                'a3':55, 'a4':Vector2(2.2, 4), 'a5':Vector3(5,6,7),
                'a6':Vector4(3,4,5,6), 'r3':Vector2(3,4), 'r4':Vector3(1,1,1),
                'r5':Vector4(11,1,1,1)}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('r1')
        self.assertAlmostEqual(val, 1.1 + 5, places=5)
        val = bs.shader.get_value('r2')
        self.assertAlmostEqual(val, 4 * 2.2, places=5)
        val = bs.shader.get_value('r3')
        self.assertAlmostEqual(val.x, 8 * 2.2, places=5)
        self.assertAlmostEqual(val.y, 8 * 4.0, places=5)
        val = bs.shader.get_value('r4')
        self.assertAlmostEqual(val.x, 1.1 * 5, places=5)
        self.assertAlmostEqual(val.y, 1.1 * 6, places=5)
        self.assertAlmostEqual(val.z, 1.1 * 7, places=5)
        val = bs.shader.get_value('r5')
        self.assertAlmostEqual(val.x, 0.5 * 3, places=5)
        self.assertAlmostEqual(val.y, 0.5 * 4, places=5)
        self.assertAlmostEqual(val.z, 0.5 * 5, places=5)
        self.assertAlmostEqual(val.w, 0.5 * 6, places=5)


if __name__ == "__main__":
    unittest.main()


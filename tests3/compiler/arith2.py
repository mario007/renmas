
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class Arith2Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
r1 = a1 + a3 * 8.0
r4 = a5 - 0.2 * (8, 8, 8)

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
        self.assertAlmostEqual(val, 1.1 + 55 * 8.0, places=4)
        val = bs.shader.get_value('r4')
        self.assertAlmostEqual(val.x, 5 - 0.2 * 8, places=4)
        self.assertAlmostEqual(val.y, 6 - 0.2 * 8, places=4)
        self.assertAlmostEqual(val.z, 7 - 0.2 * 8, places=4)

if __name__ == "__main__":
    unittest.main()


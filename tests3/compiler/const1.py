
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer
from renmas3.base import Vector2, Vector3, Vector4

class Const1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_const1(self):
        pass

        code = """
a = 555
b = -36
c = 2.3
d = -9.8
e = (2.3, 5)
f = (2.2, 4.77, -2.66)
k = (-1.23, 1.44, 9, 7.7)
        """

        props = {'a':111, 'b':250, 'c':4.4, 'd':1.1,
                'e': Vector2(2.3, 6.0), 'f': Vector3(5.6, 3.3, 2.2),
                'k': Vector4(4.4, 6.6, 2.2, 9.9)}
        bs = BasicShader(code, None, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('a')
        val2 = bs.shader.get_value('b')
        val3 = bs.shader.get_value('c')
        val4 = bs.shader.get_value('d')
        self.assertEqual(555, val)
        self.assertEqual(-36, val2)
        self.assertAlmostEqual(val3, 2.3, places=5)
        self.assertAlmostEqual(val4, -9.8, places=5)

        val5 = bs.shader.get_value('e')
        self.assertAlmostEqual(val5.x, 2.3, places=5)
        self.assertAlmostEqual(val5.y, 5.0, places=5)

        val6 = bs.shader.get_value('f')
        self.assertAlmostEqual(val6.x, 2.2, places=5)
        self.assertAlmostEqual(val6.y, 4.77, places=5)
        self.assertAlmostEqual(val6.z, -2.66, places=5)

        val7 = bs.shader.get_value('k')
        self.assertAlmostEqual(val7.x, -1.23, places=5)
        self.assertAlmostEqual(val7.y, 1.44, places=5)
        self.assertAlmostEqual(val7.z, 9.0, places=5)
        self.assertAlmostEqual(val7.w, 7.7, places=5)



if __name__ == "__main__":
    unittest.main()


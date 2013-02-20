
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class Assign1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
r1 = a1 + a2
r2 = a1 * a2 
        """
        props = {'a1':1.1, 'a2':2.2, 'r1':1.1, 'r2':3.3}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('r1')
        self.assertAlmostEqual(val, 2.2 + 1.1, places=5)
        val = bs.shader.get_value('r2')
        self.assertAlmostEqual(val, 1.1 * 2.2, places=5)

if __name__ == "__main__":
    unittest.main()



import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float
from renmas3.base import Vector2, Vector3,  Vector4

class Float2Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_float1(self):
        v = Vector2(1,1)
        v2 = Vector2(1,1)
        v3 = Vector3(1,1,1)
        v4 = Vector4(1,1,1,1)

        code = """
ret = float2(5,6)
ret2 = float2(aa, bb)
ret3 = float3(8,9.5,3)
temp = (8,9,1,2)
ret4 = float4(temp[1],5.3,6, aa)
        """
        props = {'aa':3.4, 'bb':77, 'ret':v, 'ret2':v2, 'ret3':v3, 'ret4':v4}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val.x, 5.0, places=5)
        self.assertAlmostEqual(val.y, 6.0, places=5)
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val.x, 3.4, places=5)
        self.assertAlmostEqual(val.y, 77.0, places=5)
        val = bs.shader.get_value('ret3')
        self.assertAlmostEqual(val.x, 8.0, places=5)
        self.assertAlmostEqual(val.y, 9.5, places=5)
        self.assertAlmostEqual(val.z, 3.0, places=5)
        val = bs.shader.get_value('ret4')
        self.assertAlmostEqual(val.x, 9.0, places=5)
        self.assertAlmostEqual(val.y, 5.3, places=5)
        self.assertAlmostEqual(val.z, 6.0, places=5)
        self.assertAlmostEqual(val.w, 3.4, places=5)

if __name__ == "__main__":
    unittest.main()


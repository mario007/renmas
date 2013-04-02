
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Vector3

#NOTE Test with avx!!!!
class CrossTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
ret = cross(v1, v2)
        """
        v1 = Vector3(0.32, 0.27, 0.45)
        v2 = Vector3(0.111, 0.22, 0.533)
        ret = Vector3(0.1, 0.2, 0.5)
        props = {'ret':ret, 'v1':v1, 'v2':v2}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        val2 = v1.cross(v2)
        self.assertAlmostEqual(val.x, val2.x, 4)
        self.assertAlmostEqual(val.y, val2.y, 4)
        self.assertAlmostEqual(val.z, val2.z, 4)

if __name__ == "__main__":
    unittest.main()


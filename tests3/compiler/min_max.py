
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Vector3


class MinMaxTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_max(self):

        code = """
ret = max(v1, v2)
ret2 = max(r1, r2)
        """
        v1 = Vector3(0.3, 0.2, 0.4)
        v2 = Vector3(0.1, 0.2, 0.5)
        ret = Vector3(0.0, 0.0, 0.0)
        r1 = 0.3
        r2 = 0.6
        ret2 = 0.0

        props = {'ret':ret, 'v1':v1, 'v2':v2, 'r1':r1, 'r2':r2,
                'ret2':ret2}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val.x, max(v1.x, v2.x), 5)
        self.assertAlmostEqual(val.y, max(v1.y, v2.y), 5)
        self.assertAlmostEqual(val.z, max(v1.z, v2.z), 5)
        
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val, max(r1, r2), 5)

    def test_min(self):

        code = """
ret = min(v1, v2)
ret2 = min(r1, r2)
        """
        v1 = Vector3(0.3, 0.2, 0.4)
        v2 = Vector3(0.1, 0.2, 0.5)
        ret = Vector3(0.0, 0.0, 0.0)
        r1 = 0.3
        r2 = 0.6
        ret2 = 0.0

        props = {'ret':ret, 'v1':v1, 'v2':v2, 'r1':r1, 'r2':r2,
                'ret2':ret2}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val.x, min(v1.x, v2.x), 5)
        self.assertAlmostEqual(val.y, min(v1.y, v2.y), 5)
        self.assertAlmostEqual(val.z, min(v1.z, v2.z), 5)
        
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val, min(r1, r2), 5)

if __name__ == "__main__":
    unittest.main()


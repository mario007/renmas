
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Vector3


class NormalizeTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
ret = dot(v1, v2)
        """
        v1 = Vector3(0.3, 0.2, 0.4)
        v2 = Vector3(0.1, 0.2, 0.5)
        props = {'ret':0.0, 'v1':v1, 'v2':v2}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('ret')
        val2 = v1.dot(v2)
        self.assertAlmostEqual(val, val2, 4)

if __name__ == "__main__":
    unittest.main()


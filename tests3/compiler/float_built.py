
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float

class FloatTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_float1(self):

        code = """
aa = float(55)
ret = float(bb)
ret2 = float()
        """
        props = {'aa':0.0, 'bb':77, 'ret':0.0, 'ret2':6.6}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('aa')
        self.assertAlmostEqual(val, 55.0, places=5)
        val = bs.shader.get_value('ret')
        self.assertAlmostEqual(val, 77.0, places=5)
        val = bs.shader.get_value('ret2')
        self.assertAlmostEqual(val, 0.0, places=5)

if __name__ == "__main__":
    unittest.main()


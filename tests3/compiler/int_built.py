
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float

class IntTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_int1(self):

        code = """
aa = int(-3.4)
ret = int(bb)
        """
        props = {'aa':333, 'bb':4.4, 'ret':0}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('aa')
        self.assertEqual(-3, val)
        val = bs.shader.get_value('ret')
        self.assertEqual(4, val)

if __name__ == "__main__":
    unittest.main()



import unittest

from tdasm import Runtime
from renmas3.base import BasicShader, FloatArray, FloatArray2D

class RGBATest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_item(self):
        arr = FloatArray(values=(2,3,4,5,6,7))
        code = """
index = 3
num = get_item(arr, index)
        """
        props = {'arr': arr, 'num': 2.3}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('num')
        self.assertAlmostEqual(val, 5.0, places=5)

    def test_get_item2(self):
        arr = FloatArray2D(3, 4)
        arr[1,2] = 5.0
        arr[0,1] = 1.45
        code = """
ix = 1
iy = 2
num = get_item(arr, ix, iy)
num2 = get_item(arr, 0, 1)
        """
        props = {'arr': arr, 'num': 2.3, 'num2': 1.1}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('num')
        self.assertAlmostEqual(val, 5.0, places=5)
        val = bs.shader.get_value('num2')
        self.assertAlmostEqual(val, 1.45, places=5)

if __name__ == "__main__":
    unittest.main()

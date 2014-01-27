
import unittest
from tdasm import Runtime
from sdl.shader import Shader
from sdl.args import FloatArg, register_struct
from sdl.arr import ObjArray, ArrayArg


class SuperPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

register_struct(SuperPoint, 'SuperPoint',
                fields=[('x', FloatArg), ('y', FloatArg)],
                factory=lambda: SuperPoint(1.0, 2.0))


class ArrayTests(unittest.TestCase):
    def test_array(self):

        p = SuperPoint(3.0, 4.0)
        arr = ObjArray(p)
        arr.append(p)
        arr.append(p)
        p = SuperPoint(7.0, 9.0)
        arr.append(p)

        code = """
index = 2
temp = arr[index]
p1 = temp.x
temp.y = 12.34
        """
        arg = ArrayArg('arr', arr)
        arg1 = FloatArg('p1', 4.4)
        shader = Shader(code=code, args=[arg, arg1])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()
        val = shader.get_value('p1')
        self.assertAlmostEqual(val, 7.0)
        obj = arr[2]
        self.assertAlmostEqual(obj.y, 12.34, 6)

if __name__ == "__main__":
    unittest.main()

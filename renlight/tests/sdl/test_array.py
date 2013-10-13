
import unittest
from tdasm import Runtime
from renlight.vector import Vector2, Vector3, Vector4
from renlight.sdl.shader import Shader
from renlight.sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg
from renlight.sdl.args import register_struct
from renlight.sdl.arr import Array, ArrayArg


class SuperPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

register_struct(SuperPoint, 'SuperPoint', fields=[('x', FloatArg), ('y', FloatArg)],
                factory=lambda: SuperPoint(1.0, 2.0))


class ArrayTests(unittest.TestCase):
    def test_array(self):

        p = SuperPoint(3.0, 4.0)
        arr = Array(p)
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

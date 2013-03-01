
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class Assign1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_assign1(self):

        code = """
v2[1] = v1[0]
v3[2] = 6 + 3


        """
        props = {'v1': Vector2(8.3, 6.0), 'v2': Vector3(5.6, 3.3, 2.2),
                'v3': Vector4(4.4, 6.6, 2.2, 9.9), 'ret':0.0}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        print (bs.shader._code)

        bs.execute()
        print (bs.shader.get_value('v2'))
        print (bs.shader.get_value('v3'))

if __name__ == "__main__":
    unittest.main()


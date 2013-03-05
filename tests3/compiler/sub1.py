
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class Point:
    def __init__(self, position, size, pp):
        self.position = position
        self.size = size
        self.pp = pp

    @classmethod
    def user_type(cls):
        typ_name = "Point"
        fields = [('position', Vec3), ('size', Vec2), ('pp', Vec4)]
        return (typ_name, fields)

class AssignSubscript1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_assign1(self):

        code = """
v2[1] = v1[0]
p1.position[2] = p1.size[0]

        """
        p1 = Point(Vector3(2.2, 4.4, 7.7), 
                Vector2(3.3, 5.5), Vector4(1.1, 2.2, 3.3, 4.4))
        props = {'v1': Vector2(8.3, 6.0), 'v2': Vector3(5.6, 3.3, 2.2),
                'v3': Vector4(4.4, 6.6, 2.2, 9.9), 'ret':0.0, 'p1': p1}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val1 = bs.shader.get_value('v2')
        val2 = bs.shader.get_value('v1')
        self.assertAlmostEqual(val1.y, val2.x, places=5)
        val1 = bs.shader.get_value('p1.position')
        val2 = bs.shader.get_value('p1.size')
        self.assertAlmostEqual(val1.z, val2.x, places=5)

if __name__ == "__main__":
    unittest.main()


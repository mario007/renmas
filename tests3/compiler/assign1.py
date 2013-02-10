
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type

class Point:
    def __init__(self, idx, x, y, radius, position, size, pp):
        self.idx = idx
        self.x = x
        self.y = y
        self.radius = radius
        self.position = position
        self.size = size
        self.pp = pp

    @classmethod
    def user_type(cls):
        typ_name = "Point"
        fields = [('idx', Integer), ('x', Integer), ('y', Integer),
                ('radius', Float), ('position', Vec3), ('size', Vec2),
                ('pp', Vec4)]
        return (typ_name, fields)


class Assign1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_assign1(self):

        code = """
m1 = 77
a = m1
m1 = -45
b = m1
m1 = 3.4
c = m1
m1 = -8.8
d = m1
m1 = (-8, 5.1)
e = m1
m1 = (-1, 2.25, 7)
f = m1
m1 = (8, -2.33, -7, 1)
k = m1
        """
        props = {'aa':333, 'a':111, 'b':250, 'c':4.4, 'd':1.1,
                'e': Vector2(2.3, 6.0), 'f': Vector3(5.6, 3.3, 2.2),
                'k': Vector4(4.4, 6.6, 2.2, 9.9)}
        bs = BasicShader(code, None, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('a')
        self.assertEqual(77, val)
        val = bs.shader.get_value('b')
        self.assertEqual(-45, val)
        val = bs.shader.get_value('c')
        self.assertAlmostEqual(val, 3.4, places=5)
        val = bs.shader.get_value('d')
        self.assertAlmostEqual(val, -8.8, places=5)

        val = bs.shader.get_value('e')
        self.assertAlmostEqual(val.x, -8.0, places=5)
        self.assertAlmostEqual(val.y, 5.1, places=5)

        val = bs.shader.get_value('f')
        self.assertAlmostEqual(val.x, -1.0, places=5)
        self.assertAlmostEqual(val.y, 2.25, places=5)
        self.assertAlmostEqual(val.z, 7.0, places=5)

        val = bs.shader.get_value('k')
        self.assertAlmostEqual(val.x, 8.0, places=5)
        self.assertAlmostEqual(val.y, -2.33, places=5)
        self.assertAlmostEqual(val.z, -7.0, places=5)
        self.assertAlmostEqual(val.w, 1.0, places=5)

    def test_assign2(self):
        register_user_type(Point)
        p1 = Point(33, 77, 99, 3.5, Vector3(2.2, 4.4, 7.7), 
                Vector2(3.3, 5.5), Vector4(1.1, 2.2, 3.3, 4.4))

        code = """
idx = p1.idx
p1.x = 55
pp = 555
p1.y = pp
g = 4.8
p1.radius = g
g = (4,5,6)
p1.position = g
p1.size = (6,7)
p1.pp = (8,1,3,4)


        """
        props = {'p1': p1, 'idx': 44}
        bs = BasicShader(code, None, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('idx')
        self.assertEqual(33, val)
        val = bs.shader.get_value('p1.x')
        self.assertEqual(55, val)
        val = bs.shader.get_value('p1.y')
        self.assertEqual(555, val)
        val = bs.shader.get_value('p1.radius')
        self.assertAlmostEqual(val, 4.8, places=5)
        val = bs.shader.get_value('p1.position')
        self.assertAlmostEqual(val.x, 4.0, places=5)
        self.assertAlmostEqual(val.y, 5.0, places=5)
        self.assertAlmostEqual(val.z, 6.0, places=5)
        val = bs.shader.get_value('p1.size')
        self.assertAlmostEqual(val.x, 6.0, places=5)
        self.assertAlmostEqual(val.y, 7.0, places=5)
        val = bs.shader.get_value('p1.pp')
        self.assertAlmostEqual(val.x, 8.0, places=5)
        self.assertAlmostEqual(val.y, 1.0, places=5)
        self.assertAlmostEqual(val.z, 3.0, places=5)
        self.assertAlmostEqual(val.w, 4.0, places=5)


if __name__ == "__main__":
    unittest.main()


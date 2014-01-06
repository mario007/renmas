
import unittest
from tdasm import Runtime
from sdl.vector import Vector2, Vector3, Vector4
from sdl.shader import Shader
from sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg


class IntFloatTests(unittest.TestCase):

    def test_int(self):
        code = """
temp = 5.6
p1 = int(temp)
p2 = int(8.8)
p3 = int()
p4 = int(11)
        """
        p1 = IntArg('p1', 333)
        p2 = IntArg('p2', 555)
        p3 = IntArg('p3', 555)
        p4 = IntArg('p4', 555)

        shader = Shader(code=code, args=[p1, p2, p3, p4])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertEqual(p, 5)
        p = shader.get_value('p2')
        self.assertEqual(p, 8)
        p = shader.get_value('p3')
        self.assertEqual(p, 0)
        p = shader.get_value('p4')
        self.assertEqual(p, 11)

    def test_float(self):
        code = """
temp = 5
p1 = float(temp)
p2 = float(88)
p3 = float()
p4 = float(6.6)
        """
        p1 = FloatArg('p1', 333.3)
        p2 = FloatArg('p2', 333.3)
        p3 = FloatArg('p3', 333.3)
        p4 = FloatArg('p4', 333.3)

        shader = Shader(code=code, args=[p1, p2, p3, p4])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertAlmostEqual(p, 5.0)
        p = shader.get_value('p2')
        self.assertAlmostEqual(p, 88.0)
        p = shader.get_value('p3')
        self.assertAlmostEqual(p, 0.0)
        p = shader.get_value('p4')
        self.assertAlmostEqual(p, 6.6, places=6)

    def test_float2(self):
        code = """
temp = 5
temp2 = 9.9
p1 = float2(temp, temp2)
p2 = float2(2, 3.3)
        """
        p1 = Vec2Arg('p1', Vector2(0.0, 1.0))
        p2 = Vec2Arg('p2', Vector2(0.0, 1.0))

        shader = Shader(code=code, args=[p1, p2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertAlmostEqual(p.x, 5.0)
        self.assertAlmostEqual(p.y, 9.9, places=6)
        p = shader.get_value('p2')
        self.assertAlmostEqual(p.x, 2.0)
        self.assertAlmostEqual(p.y, 3.3)

    def test_float3(self):
        code = """
temp = 5
temp2 = 9.9
p1 = float3(temp, temp2, 2)
tmp = 4.4
p2 = float3(tmp, 33, 2.1)
        """
        p1 = Vec3Arg('p1', Vector3(0.0, 1.0, 0.0))
        p2 = Vec3Arg('p2', Vector3(0.0, 1.0, 0.0))

        shader = Shader(code=code, args=[p1, p2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertAlmostEqual(p.x, 5.0)
        self.assertAlmostEqual(p.y, 9.9, places=6)
        self.assertAlmostEqual(p.z, 2.0)
        p = shader.get_value('p2')
        self.assertAlmostEqual(p.x, 4.4, places=6)
        self.assertAlmostEqual(p.y, 33.0, places=6)
        self.assertAlmostEqual(p.z, 2.1, places=6)

    def test_float4(self):
        code = """
temp = 5
temp2 = 9.9
p1 = float4(temp, temp2, 2, 5.5)
        """
        p1 = Vec4Arg('p1', Vector4(0.0, 1.0, 0.0, 0.0))

        shader = Shader(code=code, args=[p1])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertAlmostEqual(p.x, 5.0)
        self.assertAlmostEqual(p.y, 9.9, places=6)
        self.assertAlmostEqual(p.z, 2.0)
        self.assertAlmostEqual(p.w, 5.5)

if __name__ == "__main__":
    unittest.main()

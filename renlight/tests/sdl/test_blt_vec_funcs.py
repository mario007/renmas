
import unittest
from tdasm import Runtime
from renlight.vector import Vector3
from renlight.sdl.shader import Shader
from renlight.sdl.args import FloatArg, Vec3Arg


class VecFunTests(unittest.TestCase):
    def test_dot_fun(self):
        code = """
p3 = dot(p1, p2)
        """
        v1 = Vector3(2.5, 1.8, 2.9)
        v2 = Vector3(2.2, 1.1, 5.22)
        p1 = Vec3Arg('p1', v1)
        p2 = Vec3Arg('p2', v2)
        p3 = FloatArg('p3', 2.2)

        shader = Shader(code=code, args=[p1, p2, p3])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        rez = v1.dot(v2)
        p = shader.get_value('p3')
        self.assertAlmostEqual(rez, p)

    def test_normalize_fun(self):
        code = """
p2 = normalize(p1)
        """
        v1 = Vector3(2.5, 1.8, 2.9)
        v2 = Vector3(6.5, 9.8, 3.9)
        p1 = Vec3Arg('p1', v1)
        p2 = Vec3Arg('p2', v2)

        shader = Shader(code=code, args=[p1, p2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        v3 = Vector3(2.5, 1.8, 2.9)
        v3.normalize()

        p = shader.get_value('p2')
        self.assertAlmostEqual(p.x, v3.x)
        self.assertAlmostEqual(p.y, v3.y)
        self.assertAlmostEqual(p.z, v3.z)

    def test_corss_fun(self):
        code = """
p3 = cross(p1, p2)
        """
        v1 = Vector3(2.5, 1.8, 2.9)
        v2 = Vector3(2.5, 1.8, 3.9)
        v3 = Vector3(0.0, 0.0, 0.0)
        p1 = Vec3Arg('p1', v1)
        p2 = Vec3Arg('p2', v2)
        p3 = Vec3Arg('p3', v3)

        shader = Shader(code=code, args=[p1, p2, p3])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        v4 = v1.cross(v2)

        p = shader.get_value('p3')
        self.assertAlmostEqual(p.x, v4.x, places=6)
        self.assertAlmostEqual(p.y, v4.y, places=6)
        self.assertAlmostEqual(p.z, v4.z, places=6)

if __name__ == "__main__":
    unittest.main()


import unittest
from tdasm import Runtime
from sdl.vector import Vector3
from sdl.shader import Shader
from sdl.args import FloatArg, Vec3Arg, IntArg


class VecFunTests(unittest.TestCase):
    def test_abs_fun(self):
        code = """
p1 = abs(-41)
p2 = abs(-3.66)
p3 = abs((-2.5, 3.6, -1.2))
        """
        p1 = IntArg('p1', 0)
        p2 = FloatArg('p2', 0.0)
        p3 = Vec3Arg('p3', Vector3(0.0, 0.0, 0.0))

        shader = Shader(code=code, args=[p1, p2, p3])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        p = shader.get_value('p1')
        self.assertEqual(shader.get_value('p1'), 41)
        self.assertAlmostEqual(shader.get_value('p2'), 3.66, places=6)
        v =shader.get_value('p3')
        self.assertAlmostEqual(v.x, 2.5, places=6)
        self.assertAlmostEqual(v.y, 3.6, places=6)
        self.assertAlmostEqual(v.z, 1.2, places=6)


if __name__ == "__main__":
    unittest.main()

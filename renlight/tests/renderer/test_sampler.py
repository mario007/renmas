
import unittest

from tdasm import Runtime

from renlight.sdl.shader import Shader
from renlight.sdl import FloatArg, IntArg
from renlight.renderer.sampler import Sampler


class SamplerTest(unittest.TestCase):

    def test_sampler(self):
        sam = Sampler()
        sam.set_resolution(2, 2)
        sam.load('regular')
        sam.compile()
        runtimes = [Runtime()]
        sam.prepare(runtimes)

        code = """
sample = Sample()
r1 = generate_sample(sample)
p1 = sample.x
p2 = sample.y
p3 = sample.ix
p4 = sample.iy
        """

        p1 = FloatArg('p1', 566.6)
        p2 = FloatArg('p2', 566.6)

        p3 = IntArg('p3', 5655)
        p4 = IntArg('p4', 5655)
        r1 = IntArg('r1', 5655)
        args = [p1, p2, p3, p4, r1]
        shader = Shader(code=code, args=args)
        shader.compile([sam.shader])
        shader.prepare(runtimes)

        shader.execute()
        self._check_result(shader, -0.5, -0.5, 0, 0, 1)
        shader.execute()
        self._check_result(shader, 0.5, -0.5, 1, 0, 1)
        shader.execute()
        self._check_result(shader, -0.5, 0.5, 0, 1, 1)
        shader.execute()
        self._check_result(shader, 0.5, 0.5, 1, 1, 1)
        shader.execute()
        ret = shader.get_value('r1')
        self.assertEqual(ret, 0)

    def _check_result(self, shader, p1, p2, p3, p4, r1):
        t1 = shader.get_value('p1')
        self.assertEqual(t1, p1)
        t2 = shader.get_value('p2')
        self.assertEqual(t2, p2)
        t3 = shader.get_value('p3')
        self.assertAlmostEqual(t3, p3)
        t4 = shader.get_value('p4')
        self.assertAlmostEqual(t4, p4)
        k1 = shader.get_value('r1')
        self.assertEqual(k1, r1)


if __name__ == "__main__":
    unittest.main()


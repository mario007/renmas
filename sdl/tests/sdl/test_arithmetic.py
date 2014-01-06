
import unittest
from tdasm import Runtime
from sdl.vector import Vector2, Vector3, Vector4
from sdl.spectrum import RGBSpectrum, SampledSpectrum, create_samples
from sdl.shader import Shader
from sdl.args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg,\
    RGBArg, SampledArg


class ArithmeticTests(unittest.TestCase):

    def test_arithmetic(self):
        code = """
a1 = 33
a2 = 22
p1 = a1 + a2
a1 = 22.3
a2 = 11.1
p2 = a1 + a2
a1 = 44
a2 = -2.36
p3 = a1 * a2
a1 = (2.3, 4)
a2 = 5
p4 = a1 * a2

a1 = (3, 4, 6.6)
a2 = (7, 4.3, 2.6)
p5 = a1 - a2

a1 = (1, 4.1, 5.5, 9.9)
a2 = (0.22, 3.3, 2.6, 6.6)
p6 = a1 / a2
        """
        p1 = IntArg('p1', 33)
        p2 = FloatArg('p2', 55.5)
        p3 = FloatArg('p3', 55.5)
        p4 = Vec2Arg('p4', Vector2(0.0, 0.0))
        p5 = Vec3Arg('p5', Vector3(0.0, 0.0, 0.0))
        p6 = Vec4Arg('p6', Vector4(0.0, 0.0, 0.0, 0.0))

        shader = Shader(code=code, args=[p1, p2, p3, p4, p5, p6])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        rez = shader.get_value('p1')
        self.assertEqual(rez, 33 + 22)
        rez = shader.get_value('p2')
        self.assertAlmostEqual(rez, 22.3 + 11.1, places=5)
        rez = shader.get_value('p3')
        self.assertAlmostEqual(rez, 44 * -2.36, places=5)
        rez = shader.get_value('p4')
        self.assertAlmostEqual(rez.x, 5 * 2.3, places=5)
        self.assertAlmostEqual(rez.y, 5 * 4, places=5)
        rez = shader.get_value('p5')
        self.assertAlmostEqual(rez.x, 3 - 7.0, places=5)
        self.assertAlmostEqual(rez.y, 4 - 4.3, places=5)
        self.assertAlmostEqual(rez.z, 6.6 - 2.6, places=5)
        rez = shader.get_value('p6')
        self.assertAlmostEqual(rez.x, 1 / 0.22, places=5)
        self.assertAlmostEqual(rez.y, 4.1 / 3.3, places=5)
        self.assertAlmostEqual(rez.z, 5.5 / 2.6, places=5)
        self.assertAlmostEqual(rez.w, 9.9 / 6.6, places=5)

    def test_rgb_arithmetic(self):
        code = """
tmp = p1 + p2
p3 = tmp
p4 = 2 * p3
p5 = p3 * 2.66
        """
        p1 = RGBArg('p1', RGBSpectrum(0.36, 0.85, 0.14))
        p2 = RGBArg('p2', RGBSpectrum(0.22, 0.11, 0.58))
        p3 = RGBArg('p3', RGBSpectrum(0.0, 0.0, 0.0))
        p4 = RGBArg('p4', RGBSpectrum(0.0, 0.0, 0.0))
        p5 = RGBArg('p5', RGBSpectrum(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[p1, p2, p3, p4, p5])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        v = shader.get_value('p3')
        self.assertAlmostEqual(v.r, 0.36 + 0.22)
        self.assertAlmostEqual(v.g, 0.85 + 0.11)
        self.assertAlmostEqual(v.b, 0.14 + 0.58)
        v = shader.get_value('p4')
        self.assertAlmostEqual(v.r, (0.36 + 0.22) * 2, places=6)
        self.assertAlmostEqual(v.g, (0.85 + 0.11) * 2, places=6)
        self.assertAlmostEqual(v.b, (0.14 + 0.58) * 2, places=6)
        v = shader.get_value('p5')
        self.assertAlmostEqual(v.r, (0.36 + 0.22) * 2.66, places=6)
        self.assertAlmostEqual(v.g, (0.85 + 0.11) * 2.66, places=6)
        self.assertAlmostEqual(v.b, (0.14 + 0.58) * 2.66, places=6)

    def test_sampled_arithmetic(self):
        code = """
tmp = p2 + p1
p3 = tmp
p4 = p1 * 0.3
p5 = 0.22 * p2
p6 = p1 * 8
p7 = 5 * p2
        """
        vals = [(450, 0.33), (480, 0.45)]
        samples = create_samples(vals, 32, 400, 700)
        p1 = SampledArg('p1', SampledSpectrum(samples))
        vals = [(430, 0.23), (480, 0.55), (600, 0.77)]
        samples2 = create_samples(vals, 32, 400, 700)
        p2 = SampledArg('p2', SampledSpectrum(samples2))

        vals = [(430, 0.1), (480, 0.1), (600, 0.1)]
        samples3 = create_samples(vals, 32, 400, 700)
        p3 = SampledArg('p3', SampledSpectrum(samples3))

        vals = [(430, 0.1), (480, 0.1), (600, 0.1)]
        samples4 = create_samples(vals, 32, 400, 700)
        p4 = SampledArg('p4', SampledSpectrum(samples4))

        vals = [(430, 0.1), (480, 0.1), (600, 0.1)]
        samples5 = create_samples(vals, 32, 400, 700)
        p5 = SampledArg('p5', SampledSpectrum(samples5))

        vals = [(430, 0.1), (480, 0.1), (600, 0.1)]
        samples6 = create_samples(vals, 32, 400, 700)
        p6 = SampledArg('p6', SampledSpectrum(samples6))

        vals = [(430, 0.1), (480, 0.1), (600, 0.1)]
        samples7 = create_samples(vals, 32, 400, 700)
        p7 = SampledArg('p7', SampledSpectrum(samples7))

        shader = Shader(code=code, args=[p1, p2, p3, p4, p5, p6, p7])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        v = shader.get_value('p3')
        for i in range(32):
            val = samples[i] + samples2[i]
            self.assertAlmostEqual(v.samples[i], val, places=6)

        v = shader.get_value('p4')
        for i in range(32):
            self.assertAlmostEqual(v.samples[i], samples[i] * 0.3)

        v = shader.get_value('p5')
        for i in range(32):
            self.assertAlmostEqual(v.samples[i], samples2[i] * 0.22)

        v = shader.get_value('p6')
        for i in range(32):
            self.assertAlmostEqual(v.samples[i], samples[i] * 8, places=6)

        v = shader.get_value('p7')
        for i in range(32):
            self.assertAlmostEqual(v.samples[i], samples2[i] * 5, places=6)

    def test_expr(self):
        #TODO
        code = """
        """
        shader = Shader(code=code, args=[])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

if __name__ == "__main__":
    unittest.main()

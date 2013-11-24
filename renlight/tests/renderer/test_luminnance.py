
import unittest
from tdasm import Runtime

from renlight.spectrum import RGBSpectrum, SampledManager, SampledSpectrum,\
    create_samples
from renlight.renderer.spec_shaders import lum_rgb_shader, lum_sampled_shader
from renlight.sdl.shader import Shader
from renlight.sdl.args import FloatArg, RGBArg, SampledArg


class LuminnanceTests(unittest.TestCase):

    def test_rgb_lum(self):

        shader = lum_rgb_shader()
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])

        code = """
rez = lumminance(r1)
        """
        s = RGBArg('r1', RGBSpectrum(0.2, 0.3, 0.4))
        rez = FloatArg('rez', 0.0)
        shader2 = Shader(code=code, args=[rez, s])
        shader2.compile([shader])
        shader2.prepare([runtime])
        shader2.execute()

        lum = 0.2 * 0.212671 + 0.3 * 0.715160 + 0.4 * 0.072169
        val = shader2.get_value('rez')
        self.assertAlmostEqual(lum, val)

    def test_sampled_lum(self):

        mgr = SampledManager()
        shader = lum_sampled_shader(mgr)
        shader.compile()
        runtime = Runtime()
        shader.prepare([runtime])
        code = """
rez = lumminance(r1)
        """

        vals = [(450, 0.13), (480, 0.45), (620, 0.58)]
        samples = create_samples(vals, 32, 400, 700)
        sam_spec = SampledSpectrum(samples)
        s = SampledArg('r1', sam_spec)

        rez = FloatArg('rez', 0.0)
        shader2 = Shader(code=code, args=[rez, s])
        shader2.compile([shader])
        shader2.prepare([runtime])
        shader2.execute()

        val = shader2.get_value('rez')
        lum = mgr.lumminance(sam_spec)
        self.assertAlmostEqual(lum, val)

if __name__ == "__main__":
    unittest.main()

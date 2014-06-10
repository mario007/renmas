
import unittest
from tdasm import Runtime
from sdl import Shader, SampledManager,\
    RGBSpectrum, RGBArg, SampledArg, Vector3, Vec3Arg, RGBManager

from renlgt.spec_shaders import rgb_to_spectrum_shader


class RgbToSpectrumTest(unittest.TestCase):

    def test_rgb_to_rgb_spectrum(self):
        runtimes = [Runtime()]

        color_mgr = RGBManager()
        rgb_to_spec = rgb_to_spectrum_shader(color_mgr)
        rgb_to_spec.compile(color_mgr=color_mgr)
        rgb_to_spec.prepare(runtimes)

        code = """
spec = rgb_to_spectrum(color)
        """
        val = Vector3(0.3, 0.5, 0.7)
        col = Vec3Arg('color', val)
        spec = RGBArg('spec', RGBSpectrum(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[col, spec])
        shader.compile(shaders=[rgb_to_spec], color_mgr=color_mgr)
        shader.prepare(runtimes)
        shader.execute()

        value = shader.get_value('spec')
        self.assertAlmostEqual(value.r, val.x)
        self.assertAlmostEqual(value.g, val.y)
        self.assertAlmostEqual(value.b, val.z)

    def test_rgb_to_sampled_spectrum(self):
        runtimes = [Runtime()]

        color_mgr = SampledManager()
        rgb_to_spec = rgb_to_spectrum_shader(color_mgr)
        rgb_to_spec.compile(color_mgr=color_mgr)
        rgb_to_spec.prepare(runtimes)

        code = """
spec = rgb_to_spectrum(color)
        """
        val = Vector3(0.3, 0.5, 0.7)
        col = Vec3Arg('color', val)
        spec = SampledArg('spec', color_mgr.zero())
        shader = Shader(code=code, args=[col, spec])
        shader.compile(shaders=[rgb_to_spec], color_mgr=color_mgr)
        shader.prepare(runtimes)
        shader.execute()

        value = shader.get_value('spec')
        vv = color_mgr.rgb_to_sampled(RGBSpectrum(val.x, val.y, val.z))
        for i in range(len(value.samples)):
            self.assertAlmostEqual(value.samples[i], vv.samples[i], places=6)


if __name__ == "__main__":
    unittest.main()

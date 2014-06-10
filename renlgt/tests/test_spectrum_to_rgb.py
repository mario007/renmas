
import unittest
from tdasm import Runtime
from sdl import Shader, SampledManager, Vector3, Vec3Arg,\
    RGBSpectrum, RGBArg, SampledArg, RGBManager
from renlgt.spec_shaders import spectrum_to_rgb_shader


class SpectrumToRGBTest(unittest.TestCase):
    def test_rgb_to_rgb(self):
        runtimes = [Runtime()]

        color_mgr = RGBManager()
        s_to_rgb = spectrum_to_rgb_shader(color_mgr)
        s_to_rgb.compile(color_mgr=color_mgr)
        s_to_rgb.prepare(runtimes)

        code = """
value = spectrum_to_rgb(color)
        """
        spec = RGBSpectrum(0.3, 0.5, 0.4)
        col = RGBArg('color', spec)
        val = Vec3Arg('value', Vector3(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[col, val])
        shader.compile(shaders=[s_to_rgb], color_mgr=color_mgr)
        shader.prepare(runtimes)
        shader.execute()

        value = shader.get_value('value')
        self.assertAlmostEqual(value.x, 0.3)
        self.assertAlmostEqual(value.y, 0.5)
        self.assertAlmostEqual(value.z, 0.4)

    def test_sampled_to_rgb(self):
        runtimes = [Runtime()]

        color_mgr = SampledManager()
        s_to_rgb = spectrum_to_rgb_shader(color_mgr)
        s_to_rgb.compile(color_mgr=color_mgr)
        s_to_rgb.prepare(runtimes)

        code = """
value = spectrum_to_rgb(color)
        """
        spec = RGBSpectrum(0.3, 0.5, 0.4)
        spec = color_mgr.rgb_to_sampled(spec)
        col = SampledArg('color', spec)
        val = Vec3Arg('value', Vector3(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[col, val])
        shader.compile(shaders=[s_to_rgb], color_mgr=color_mgr)
        shader.prepare(runtimes)
        shader.execute()

        value = shader.get_value('value')
        vv = color_mgr.sampled_to_rgb(spec)
        self.assertAlmostEqual(value.x, vv.r)
        self.assertAlmostEqual(value.y, vv.g)
        self.assertAlmostEqual(value.z, vv.b, places=6)


if __name__ == "__main__":
    unittest.main()

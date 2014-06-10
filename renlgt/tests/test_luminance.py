
import unittest
from tdasm import Runtime
from sdl import Shader, SampledManager,\
    RGBSpectrum, RGBArg, SampledArg, RGBManager, FloatArg
from renlgt.spec_shaders import luminance_shader


class LuminanceTest(unittest.TestCase):
    def test_rgb_luminance(self):
        runtimes = [Runtime()]

        color_mgr = RGBManager()
        lum_shader = luminance_shader(color_mgr)
        lum_shader.compile(color_mgr=color_mgr)
        lum_shader.prepare(runtimes)

        code = """
value = luminance(color)
        """
        spec = RGBSpectrum(0.3, 0.5, 0.7)
        col = RGBArg('color', spec)
        val = FloatArg('value', 0.0)
        shader = Shader(code=code, args=[col, val])
        shader.compile(shaders=[lum_shader], color_mgr=color_mgr)
        shader.prepare(runtimes)
        shader.execute()

        value = shader.get_value('value')
        vv = color_mgr.luminance(spec)
        self.assertAlmostEqual(value, vv)

    def test_sampled_luminance(self):
        runtimes = [Runtime()]

        color_mgr = SampledManager()
        lum_shader = luminance_shader(color_mgr)
        lum_shader.compile(color_mgr=color_mgr)
        lum_shader.prepare(runtimes)

        code = """
value = luminance(color)
        """
        spec = RGBSpectrum(0.3, 0.5, 0.7)
        spec = color_mgr.rgb_to_sampled(spec)
        col = SampledArg('color', spec)
        val = FloatArg('value', 0.0)
        shader = Shader(code=code, args=[col, val])
        shader.compile(shaders=[lum_shader], color_mgr=color_mgr)
        shader.prepare(runtimes)
        shader.execute()

        value = shader.get_value('value')
        vv = color_mgr.luminance(spec)
        self.assertAlmostEqual(value, vv)


if __name__ == "__main__":
    unittest.main()


import unittest
from tdasm import Runtime
from renlgt.light import GeneralLight
from renlgt.shadepoint import register_sampled_shadepoint,\
    register_rgb_shadepoint
from sdl import PointerArg, Shader, SampledManager,\
    RGBSpectrum, RGBArg, SampledArg, Vector3, Vec3Arg

from renlgt.spec_shaders import vec_to_rgb_shader, vec_to_sampled_shader


class RgbToSpectrumTest(unittest.TestCase):

    def atest_rgb_to_rgb_spectrum(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime()]
        rgb_to_shader = vec_to_rgb_shader()
        rgb_to_shader.compile()
        rgb_to_shader.prepare(runtimes)
        

        code = """
rgb_color = float3(0.4, 0.6, 0.8)
tmp = rgb_to_spectrum(rgb_color)
ret = tmp

        """
        rgb_arg = RGBArg('ret', RGBSpectrum(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[rgb_arg])
        shader.compile([rgb_to_shader])
        shader.prepare(runtimes)
        shader.execute()
        val = shader.get_value('ret')
        print(val)

    def test_rgb_to_sampled_spectrum(self):
        sam_mgr = SampledManager()
        register_sampled_shadepoint(sam_mgr)

        runtimes = [Runtime()]
        rgb_to_shader = vec_to_sampled_shader(sam_mgr)
        rgb_to_shader.compile()
        rgb_to_shader.prepare(runtimes)

        #print(rgb_to_shader._asm_code)
        code = """
rgb_color = float3(0.4, 0.6, 0.8)
tmp = rgb_to_spectrum(rgb_color)
#ret = tmp

        """
        sampled_arg = SampledArg('ret', sam_mgr.zero())
        shader = Shader(code=code, args=[sampled_arg])
        shader.compile([rgb_to_shader])
        shader.prepare(runtimes)
        shader.execute()
        val = shader.get_value('ret')
        print(val)


if __name__ == "__main__":
    unittest.main()

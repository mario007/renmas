
import unittest
from tdasm import Runtime
from renlgt.light import GeneralLight, LightManager
from renlgt.shadepoint import register_sampled_shadepoint,\
    register_rgb_shadepoint
from sdl import PointerArg, Shader, SampledManager,\
    RGBSpectrum, RGBArg, SampledArg, Vector3, Vec3Arg


class LightTest(unittest.TestCase):

    def test_light_manager(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime()]
        lgt = GeneralLight()
        lgt.load('point', sam_mgr, spectral=False)

        mgr = LightManager()
        mgr.add('light1', lgt)

        mgr.compile_shaders(sam_mgr, spectral=False)


if __name__ == "__main__":
    unittest.main()

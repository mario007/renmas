
import unittest
from tdasm import Runtime
from renlgt.light import GeneralLight, LightManager
from renlgt.shadepoint import register_rgb_shadepoint
from sdl import Shader, SampledManager,\
    RGBSpectrum, Vector3, Vec3Arg, IntArg


class LightMgrTest(unittest.TestCase):

    def test_light_manager(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime(), Runtime()]
        lgt = GeneralLight()
        lgt.load('point', sam_mgr, spectral=False)

        lgt2 = GeneralLight()
        lgt2.load('point', sam_mgr, spectral=False)
        lgt2.set_value('intensity', RGBSpectrum(0.3, 0.3, 0.3))
        lgt2.set_value('position', Vector3(2.0, 2.0, 2.0))

        mgr = LightManager()
        mgr.add('light1', lgt)
        mgr.add('light2', lgt2)

        mgr.compile_shaders(sam_mgr, spectral=False)
        mgr.prepare_shaders(runtimes)

        code = """
hp = HitPoint()
hp.hit = (4.0, 5, 6)
sp = ShadePoint()
light_radiance(hp, sp, 1)
wi = sp.wi
n = number_of_lights()
        """
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        nlights = IntArg('n', 999)
        shader = Shader(code=code, args=[wi, nlights])
        shader.compile(shaders=[mgr.rad_shader, mgr.nlights_shader])
        shader.prepare(runtimes)
        shader.execute()

        wi = Vector3(2.0, 2.0, 2.0) - Vector3(4.0, 5.0, 6.0)
        wi.normalize()
        wi_s = shader.get_value('wi')
        self.assertAlmostEqual(wi.x, wi_s.x)
        self.assertAlmostEqual(wi.y, wi_s.y)
        self.assertAlmostEqual(wi.z, wi_s.z)

        self.assertEqual(2, shader.get_value('n'))


if __name__ == "__main__":
    unittest.main()

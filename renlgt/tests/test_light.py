
import unittest
from tdasm import Runtime
from renlgt.light import GeneralLight
from renlgt.shadepoint import register_sampled_shadepoint,\
    register_rgb_shadepoint
from sdl import PointerArg, Shader, SampledManager,\
    RGBSpectrum, RGBArg, SampledArg, Vector3, Vec3Arg


class LightTest(unittest.TestCase):

    def test_rgb_point_light(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime()]
        lgt = GeneralLight()
        lgt.load('point', sam_mgr, spectral=False)
        lgt.set_value('intensity', RGBSpectrum(0.3, 0.3, 0.3))
        lgt.set_value('position', Vector3(2.0, 2.0, 2.0))
        lgt.compile()
        lgt.prepare(runtimes)
        ptrs = lgt.shader.get_ptrs()

        ptr_func = PointerArg('ptr_func', ptrs[0])
        spec = RGBArg('spec', RGBSpectrum(0.5, 0.5, 0.5))
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        pos = Vec3Arg('position', Vector3(0.0, 0.0, 0.0))

        code = """
hp = HitPoint()
hp.hit = (4.0, 5, 6)
sp = ShadePoint()
__light_radiance(hp, sp, ptr_func)
spec = sp.light_intensity
wi = sp.wi
position = sp.light_position
        """
        shader = Shader(code=code, args=[ptr_func, wi, spec, pos])
        shader.compile()
        shader.prepare(runtimes)
        shader.execute()

        wi = Vector3(2.0, 2.0, 2.0) - Vector3(4.0, 5.0, 6.0)
        wi.normalize()
        wi_s = shader.get_value('wi')
        self.assertAlmostEqual(wi.x, wi_s.x)
        self.assertAlmostEqual(wi.y, wi_s.y)
        self.assertAlmostEqual(wi.z, wi_s.z)

        p = Vector3(2.0, 2.0, 2.0)
        p_s = shader.get_value('position')
        self.assertAlmostEqual(p.x, p_s.x)
        self.assertAlmostEqual(p.y, p_s.y)
        self.assertAlmostEqual(p.z, p_s.z)

        s_s = shader.get_value('spec')
        s = RGBSpectrum(0.3, 0.3, 0.3)
        self.assertAlmostEqual(s.r, s_s.r)
        self.assertAlmostEqual(s.g, s_s.g)
        self.assertAlmostEqual(s.b, s_s.b)

    def test_sampled_point_light(self):
        sam_mgr = SampledManager()
        register_sampled_shadepoint(sam_mgr)

        runtimes = [Runtime()]
        lgt = GeneralLight()
        lgt.load('point', sam_mgr, spectral=True)
        lgt.set_value('intensity', RGBSpectrum(0.3, 0.3, 0.3))
        lgt.set_value('position', Vector3(2.0, 2.0, 2.0))
        lgt.compile()
        lgt.prepare(runtimes)
        ptrs = lgt.shader.get_ptrs()

        ptr_func = PointerArg('ptr_func', ptrs[0])
        spec = SampledArg('spec', sam_mgr.zero())
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        pos = Vec3Arg('position', Vector3(0.0, 0.0, 0.0))

        code = """
hp = HitPoint()
hp.hit = (4.0, 5, 6)
sp = ShadePoint()
__light_radiance(hp, sp, ptr_func)
spec = sp.light_intensity
wi = sp.wi
position = sp.light_position
        """
        shader = Shader(code=code, args=[ptr_func, wi, spec, pos])
        shader.compile()
        shader.prepare(runtimes)
        shader.execute()

        wi = Vector3(2.0, 2.0, 2.0) - Vector3(4.0, 5.0, 6.0)
        wi.normalize()
        wi_s = shader.get_value('wi')
        self.assertAlmostEqual(wi.x, wi_s.x)
        self.assertAlmostEqual(wi.y, wi_s.y)
        self.assertAlmostEqual(wi.z, wi_s.z)

        p = Vector3(2.0, 2.0, 2.0)
        p_s = shader.get_value('position')
        self.assertAlmostEqual(p.x, p_s.x)
        self.assertAlmostEqual(p.y, p_s.y)
        self.assertAlmostEqual(p.z, p_s.z)

        s = sam_mgr.rgb_to_sampled(RGBSpectrum(0.3, 0.3, 0.3), illum=True)
        s_s = shader.get_value('spec')

        for i in range(len(s.samples)):
            self.assertAlmostEqual(s.samples[i], s_s.samples[i])

if __name__ == "__main__":
    unittest.main()

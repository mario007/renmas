
import unittest
from tdasm import Runtime
from renlgt.light import GeneralLight, AreaLight
from renlgt.shadepoint import register_sampled_shadepoint,\
    register_rgb_shadepoint
from sdl import PointerArg, Shader, SampledManager,\
    RGBSpectrum, RGBArg, SampledArg, Vector3, Vec3Arg, FloatArg
from renlgt.rectangle import Rectangle
from renlgt.material import Material


class AreaLightTest(unittest.TestCase):

    def test_rgb_area_light(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        point = Vector3(0.0, 0.0, 55.92)
        e1 = Vector3(55.28, 0.0, 0.0)
        e2 = Vector3(0.0, 54.88, 0.0)
        normal = Vector3(0.0, 0.0, -1.0)
        rectangle = Rectangle(point, e1, e2, normal)

        material = Material()
        material.load('lambertian_emiter', sam_mgr)
        e = RGBSpectrum(0.5, 0.5, 0.5)
        material.set_value('emission', e)

        runtimes = [Runtime()]
        lgt = AreaLight(shape=rectangle, material=material)
        lgt.load('general', sam_mgr, spectral=False)
        lgt.compile()
        lgt.prepare(runtimes)
        ptrs = lgt.shader.get_ptrs()

        ptr_func = PointerArg('ptr_func', ptrs[0])
        spec = RGBArg('spec', RGBSpectrum(0.5, 0.5, 0.5))
        wi = Vec3Arg('wi', Vector3(0.0, 0.0, 0.0))
        pos = Vec3Arg('position', Vector3(0.0, 0.0, 0.0))
        n = Vec3Arg('normal', Vector3(0.0, 0.0, 0.0))
        pdf = FloatArg('pdf', 0.0)
        emission = RGBArg('emission', RGBSpectrum(0.0, 0.0, 0.0))

        code = """
hp = HitPoint()
hp.hit = (4.0, 5, 6)
sp = ShadePoint()
__light_radiance(hp, sp, ptr_func)
spec = sp.light_intensity
wi = sp.wi
position = sp.light_position
normal = sp.light_normal
pdf = sp.light_pdf
emission = sp.material_emission
        """

        shader = Shader(code=code, args=[ptr_func, wi, spec, pos, n, pdf,
                        emission])
        shader.compile()
        shader.prepare(runtimes)
        shader.execute()

        print("Position ", shader.get_value('position'))
        print("Normal ", shader.get_value('normal'))
        print("Light pdf ", shader.get_value('pdf'))
        print("Emission ", shader.get_value('emission'))
        print("Wi ", shader.get_value('wi'))
        print("Intensity ", shader.get_value('spec'))

if __name__ == "__main__":
    unittest.main()

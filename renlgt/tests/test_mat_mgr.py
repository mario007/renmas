
import unittest
import math
from tdasm import Runtime
from renlgt.material import Material, MaterialManager
from renlgt.shadepoint import register_rgb_shadepoint
from sdl import Shader, SampledManager, RGBSpectrum, RGBArg


class MaterialMgrTest(unittest.TestCase):

    def test_material_manager(self):
        sam_mgr = SampledManager()
        register_rgb_shadepoint()

        runtimes = [Runtime(), Runtime()]
        mat = Material()
        mat.load('lambertian', sam_mgr, spectral=False)
        mat.set_value('diffuse', RGBSpectrum(0.2, 0.3, 0.4))

        mgr = MaterialManager()
        mgr.add('material1', mat)

        mgr.compile_shaders(sam_mgr, spectral=False)
        mgr.prepare_shaders(runtimes)

        code = """
hp = HitPoint()
sp = ShadePoint()
material_reflectance(hp, sp, 0)
spec = sp.material_reflectance
        """
        spec = RGBArg('spec', RGBSpectrum(0.5, 0.5, 0.5))
        shader = Shader(code=code, args=[spec])
        shader.compile(shaders=[mgr.ref_shader])
        shader.prepare(runtimes)
        shader.execute()

        s = shader.get_value('spec')
        ls = RGBSpectrum(0.2, 0.3, 0.4) * (1.0 / math.pi)

        self.assertAlmostEqual(s.r, ls.r)
        self.assertAlmostEqual(s.g, ls.g)
        self.assertAlmostEqual(s.b, ls.b)


if __name__ == "__main__":
    unittest.main()

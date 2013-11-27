
import unittest

from tdasm import Runtime

from renlight.vector import Vector3
from renlight.sdl.shader import Shader
from renlight.sdl.args import Vec3Arg, PointerArg, RGBArg 

from renlight.renderer.shadepoint import register_rgb_shadepoint, register_sampled_shadepoint
from renlight.spectrum import RGBSpectrum
from renlight.renderer.mat_mgr import Material


class MaterialTest(unittest.TestCase):

    def test_rgb_lambertian(self):
        register_rgb_shadepoint()
        mat = Material()
        r = RGBSpectrum(0.0, 0.0, 0.0)
        mat.load('lambertian', r)
        mat.compile()
        runtime = Runtime()
        mat.prepare([runtime])
        ptrs = mat.bsdf.get_ptrs()

        code = """
hp = HitPoint()
sp = ShadePoint()
material_reflectance(hp, sp, ptr_func)
rez = sp.material_reflectance
        """
        ptr_func = PointerArg('ptr_func', ptrs[0])
        rez = RGBArg('rez', RGBSpectrum(0.0, 0.0, 0.0))
        shader = Shader(code=code, args=[ptr_func, rez])
        shader.compile()
        shader.prepare([runtime])
        shader.execute()

        print(shader.get_value('rez'))

if __name__ == "__main__":
    unittest.main()

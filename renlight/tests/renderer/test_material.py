
import unittest

from tdasm import Runtime

from renlight.vector import Vector3
from renlight.sdl.shader import Shader
from renlight.sdl.args import Vec3Arg, PointerArg 

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
        print(ptrs)

        code = """
hp = HitPoint()
sp = ShadePoint()
call_indirect(hp, sp, ptr_func)
        """
        ptr_func = PointerArg('ptr_func', ptrs[0])
        shader = Shader(code=code, args=[ptr_func])
        #shader.compile()

if __name__ == "__main__":
    unittest.main()

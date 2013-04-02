
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager
from renmas3.renderer import SurfaceShader, Material, MaterialManager, ShadePoint

class Assign1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_assign1(self):

        code = """
shadepoint.light_intensity = spectrum(0.25)
        """
        props = {}
        col_mgr = ColorManager(spectral=True)
        brdf = SurfaceShader(code, props, col_mgr=col_mgr)
        mat = Material(bsdf=brdf)
        mgr = MaterialManager()
        mgr.add('blue_velvet', mat)
        runtime = Runtime()
        runtime2 = Runtime()
        runtimes = [runtime, runtime2]

        #bs.prepare([runtime])
        shader = mgr.prepare_bsdf('brdf', runtimes)
        #print (bs.shader._code)

        #bs.execute()
        sh = ShadePoint()
        code = """
hp = Hitpoint()
sp = Shadepoint()
brdf(hp, sp, 0)
spec = sp.light_intensity
        """
        spec = col_mgr.black()
        props = {'spec': spec}
        bs = BasicShader(code, props, col_mgr=col_mgr)
        bs.prepare(runtimes, shaders=[shader])
        print (bs.shader._code)

        bs.execute()

        print(bs.shader.get_value('spec'))



if __name__ == "__main__":
    unittest.main()


import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager


class SpectrumToRGBTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_spec_to_rgb(self):

        code = """
vec = spectrum_to_rgb(spec1)

        """
        rgb = RGBSpectrum(0.2, 0.3, 0.2)
        vec = Vector3(0.0, 0.0, 0.0)
        props = {'spec1':rgb, 'vec':vec}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('vec')
        val2 = col_mgr.to_RGB(rgb)
        self.assertAlmostEqual(val.x, val2.r, places=5)
        self.assertAlmostEqual(val.y, val2.g, places=5)
        self.assertAlmostEqual(val.z, val2.b, places=5)

    def test_sampled_spec_to_rgb(self):

        code = """
vec = spectrum_to_rgb(spec1)
        """
        col_mgr = ColorManager(spectral=True)
        rgb = col_mgr.create_spectrum((0.2, 0.3, 0.2))

        vec = Vector3(0.0, 0.0, 0.0)
        props = {'spec1':rgb, 'vec':vec}
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('vec')
        val2 = col_mgr.to_RGB(rgb)
        self.assertAlmostEqual(val.x, val2.r, places=5)
        self.assertAlmostEqual(val.y, val2.g, places=5)
        self.assertAlmostEqual(val.z, val2.b, places=5)

if __name__ == "__main__":
    unittest.main()

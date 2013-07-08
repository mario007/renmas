
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

    def test_rgb_to_spec(self):

        code = """
spec1 = rgb_to_spectrum(vec)

        """
        rgb = RGBSpectrum(0.0, 0.0, 0.0)
        vec = Vector3(0.2, 0.3, 0.2)
        props = {'spec1':rgb, 'vec':vec}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)

        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('spec1')
        self.assertAlmostEqual(vec.x, val.r, places=5)
        self.assertAlmostEqual(vec.y, val.g, places=5)
        self.assertAlmostEqual(vec.z, val.b, places=5)

    def test_rgb_to_spec2(self):

        code = """
spec1 = rgb_to_spectrum(vec)

        """
        vec = Vector3(0.2, 0.3, 0.2)
        col_mgr = ColorManager(spectral=True)
        rgb = col_mgr.black()
        props = {'spec1':rgb, 'vec':vec}
        bs = BasicShader(code, props, col_mgr=col_mgr)

        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('spec1')
        val2 = col_mgr.create_spectrum((0.2, 0.3, 0.2), illum=False)
        for i in range(len(val2.samples)):
            self.assertAlmostEqual(val.samples[i], val2.samples[i], places=5)


if __name__ == "__main__":
    unittest.main()

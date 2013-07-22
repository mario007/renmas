
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager

class ChromacityToSpectrumTest(unittest.TestCase):
    def setUp(self):
        pass


    def test_chromacity_to_rgb(self):

        code = """
spec1 = chromacity_to_spectrum(0.41, 0.45)

        """
        rgb = RGBSpectrum(0.0, 0.0, 0.0)
        props = {'spec1':rgb}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)

        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        spec2 = col_mgr.chromacity_to_spectrum(0.41, 0.45)

        val = bs.shader.get_value('spec1')
        self.assertAlmostEqual(spec2.r, val.r, places=4)
        self.assertAlmostEqual(spec2.g, val.g, places=4)
        self.assertAlmostEqual(spec2.b, val.b, places=4)

    def test_chromacity_to_spec(self):

        code = """
spec1 = chromacity_to_spectrum(0.41, 0.45)

        """
        col_mgr = ColorManager(spectral=True)
        rgb = col_mgr.black()
        props = {'spec1':rgb}
        bs = BasicShader(code, props, col_mgr=col_mgr)

        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        spec2 = col_mgr.chromacity_to_spectrum(0.41, 0.45)

        val = bs.shader.get_value('spec1')
        for i in range(len(val.samples)):
            self.assertAlmostEqual(val.samples[i], spec2.samples[i], places=4)

if __name__ == "__main__":
    unittest.main()


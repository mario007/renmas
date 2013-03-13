
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager


class SpectrumTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_spec1(self):

        code = """
spec = spectrum(0.3)
        """
        rgb = RGBSpectrum(0.0, 0.0, 0.0)
        props = {'spec': rgb}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('spec')
        self.assertAlmostEqual(val.r, 0.3, 4)
        self.assertAlmostEqual(val.g, 0.3, 4)
        self.assertAlmostEqual(val.b, 0.3, 4)

    def test_spec2(self):

        code = """
spec = spectrum(0.2)
        """
        col_mgr = ColorManager(spectral=True)
        rgb = col_mgr.create_spectrum((0.2, 0.3, 0.2))
        props = {'spec':rgb}
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('spec')
        nsamples = col_mgr.nsamples
        for i in range(nsamples):
            self.assertAlmostEqual(val.samples[i], 0.2, places=5)

if __name__ == "__main__":
    unittest.main()

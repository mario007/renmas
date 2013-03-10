import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager

class ArithSpec1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_arith1(self):

        code = """
spec3 = spec1 + spec2
spec4 = spec1 * 4
spec5 = 8 * spec2
        """
        rgb = RGBSpectrum(0.2, 0.3, 0.2)
        rgb2 = RGBSpectrum(0.1, 0.2, 0.3)
        rgb3 = RGBSpectrum(0.0, 0.0, 0.0)
        rgb4 = RGBSpectrum(0.0, 0.0, 0.0)
        rgb5 = RGBSpectrum(0.0, 0.0, 0.0)
        props = {'spec1':rgb, 'spec2':rgb2, 'spec3':rgb3, 'spec4':rgb4,
                'spec5':rgb5}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val1 = bs.shader.get_value('spec3')
        self.assertAlmostEqual(val1.r, 0.2+0.1, places=5)
        self.assertAlmostEqual(val1.g, 0.3+0.2, places=5)
        self.assertAlmostEqual(val1.b, 0.2+0.3, places=5)
        val1 = bs.shader.get_value('spec4')
        self.assertAlmostEqual(val1.r, 0.2*4, places=5)
        self.assertAlmostEqual(val1.g, 0.3*4, places=5)
        self.assertAlmostEqual(val1.b, 0.2*4, places=5)
        val1 = bs.shader.get_value('spec5')
        self.assertAlmostEqual(val1.r, 0.1*8, places=5)
        self.assertAlmostEqual(val1.g, 0.2*8, places=5)
        self.assertAlmostEqual(val1.b, 0.3*8, places=5)

    def test_arith2(self):
        code = """
spec3 = spec1 + spec2
spec4 = spec1 * 0.3
spec5 = 2 * spec2
        """

        nsamples = 32
        rgb = SampledSpectrum([0.1]*nsamples)
        rgb2 = SampledSpectrum([0.2]*nsamples)
        rgb3 = SampledSpectrum([0.3]*nsamples)
        rgb4 = SampledSpectrum([0.4]*nsamples)
        rgb5 = SampledSpectrum([0.5]*nsamples)

        props = {'spec1':rgb, 'spec2':rgb2, 'spec3':rgb3, 'spec4':rgb4, 'spec5':rgb5}
        col_mgr = ColorManager(spectral=True)
        col_mgr._nsamples = 32 #NOTE HACK - just for testing spectrum asm commands 
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = bs.shader.get_value('spec3')
        for i in range(nsamples):
            self.assertAlmostEqual(val.samples[i], rgb.samples[i] + rgb2.samples[i], places=5)
        val = bs.shader.get_value('spec4')
        for i in range(nsamples):
            self.assertAlmostEqual(val.samples[i], rgb.samples[i] * 0.3, places=5)
        val = bs.shader.get_value('spec5')
        for i in range(nsamples):
            self.assertAlmostEqual(val.samples[i], rgb2.samples[i] * 2, places=5)

if __name__ == "__main__":
    unittest.main()


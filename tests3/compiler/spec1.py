
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager

class ShadePoint:
    def __init__(self, spectrum1, spectrum2):
        self.spectrum1 = spectrum1
        self.spectrum2 = spectrum2

    @classmethod
    def user_type(cls):
        typ_name = "ShadePoint"
        fields = [('spectrum1', Spectrum), ('spectrum2', Spectrum)]
        return (typ_name, fields)

class Assign1Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_assign1(self):

        code = """
p = spec1
spec2 = p

        """
        rgb = RGBSpectrum(0.2, 0.3, 0.2)
        rgb2 = RGBSpectrum(0.1, 0.8, 0.9)
        props = {'spec1':rgb, 'spec2':rgb2}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val1 = bs.shader.get_value('spec1')
        val2 = bs.shader.get_value('spec2')
        self.assertAlmostEqual(val1.r, val2.r, places=5)
        self.assertAlmostEqual(val1.g, val2.g, places=5)
        self.assertAlmostEqual(val1.b, val2.b, places=5)

    def test_assign2(self):

        code = """
p = spec1
spec2 = p

        """
        nsamples = 32 
        rgb = SampledSpectrum([0.1]*nsamples)
        rgb2 = SampledSpectrum([0.2]*nsamples)
        col_mgr = ColorManager(spectral=True)
        col_mgr._nsamples = 32 #NOTE HACK - just for testing spectrum asm commands 

        props = {'spec1':rgb, 'spec2':rgb2}
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val1 = bs.shader.get_value('spec1')
        val2 = bs.shader.get_value('spec2')
        for i in range(nsamples):
            self.assertAlmostEqual(val1.samples[i], val2.samples[i], places=5)

    def test_assign3(self):
        code = """
spec1 = sh.spectrum1
sh.spectrum2 = spec2
        """
        rgb = RGBSpectrum(0.2, 0.3, 0.2)
        rgb2 = RGBSpectrum(0.1, 0.8, 0.9)
        rgb3 = RGBSpectrum(0.5, 0.3, 0.1)
        rgb4 = RGBSpectrum(0.1, 0.2, 0.2)
        sh = ShadePoint(rgb3, rgb4)
        props = {'spec1':rgb, 'spec2':rgb2, 'sh': sh}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val1 = bs.shader.get_value('spec1')
        val2 = bs.shader.get_value('sh.spectrum1')
        self.assertAlmostEqual(val1.r, val2.r, places=5)
        self.assertAlmostEqual(val1.g, val2.g, places=5)
        self.assertAlmostEqual(val1.b, val2.b, places=5)
        val1 = bs.shader.get_value('spec2')
        val2 = bs.shader.get_value('sh.spectrum2')
        self.assertAlmostEqual(val1.r, val2.r, places=5)
        self.assertAlmostEqual(val1.g, val2.g, places=5)
        self.assertAlmostEqual(val1.b, val2.b, places=5)

    def test_assign4(self):
        code = """
spec1 = sh.spectrum1
sh.spectrum2 = spec2
        """

        nsamples = 32
        rgb = SampledSpectrum([0.1]*nsamples)
        rgb2 = SampledSpectrum([0.2]*nsamples)
        rgb3 = SampledSpectrum([0.3]*nsamples)
        rgb4 = SampledSpectrum([0.4]*nsamples)

        sh = ShadePoint(rgb3, rgb4)
        props = {'spec1':rgb, 'spec2':rgb2, 'sh': sh}
        col_mgr = ColorManager(spectral=True)
        col_mgr._nsamples = 32 #NOTE HACK - just for testing spectrum asm commands 
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val1 = bs.shader.get_value('spec1')
        val2 = bs.shader.get_value('sh.spectrum1')
        for i in range(nsamples):
            self.assertAlmostEqual(val1.samples[i], val2.samples[i], places=5)
        val1 = bs.shader.get_value('spec2')
        val2 = bs.shader.get_value('sh.spectrum2')
        for i in range(nsamples):
            self.assertAlmostEqual(val1.samples[i], val2.samples[i], places=5)

if __name__ == "__main__":
    unittest.main()


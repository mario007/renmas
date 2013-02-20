import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import register_user_type, create_user_type
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum

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
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        print (bs.shader._code)

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

if __name__ == "__main__":
    unittest.main()


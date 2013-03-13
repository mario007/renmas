
import unittest
from tdasm import Runtime
from renmas3.base import BasicShader, Integer, Float, Vec3, Vec2, Vec4
from renmas3.base import Vector2, Vector3, Vector4, Struct
from renmas3.base import RGBSpectrum, SampledSpectrum, Spectrum
from renmas3.base import ColorManager


class LuminanceTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_lum1(self):
        code = """
ret1 = luminance(v1)
ret2 = luminance(v2)
        """
        v1 = Vector3(0.2, 0.3, 0.4)
        v2 = Vector4(0.4, 0.1, 0.2, 0.5)
        props = {'v1':v1, 'v2':v2, 'ret1':0.0, 'ret2':0.0}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        lum1 = v1.x * 0.2126 + v1.y * 0.7152 + v1.z * 0.0722
        lum2 = bs.shader.get_value('ret1')
        lum3 = v2.x * 0.2126 + v2.y * 0.7152 + v2.z * 0.0722
        lum4 = bs.shader.get_value('ret2')

        self.assertAlmostEqual(lum1, lum2, places=5)
        self.assertAlmostEqual(lum3, lum4, places=5)


    def test_lum2(self):

        code = """
ret = luminance(spec1)
        """
        rgb = RGBSpectrum(0.2, 0.3, 0.2)
        props = {'spec1':rgb, 'ret':0.0}
        col_mgr = ColorManager(spectral=False)
        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        lum1 = col_mgr.Y(rgb)
        lum2 = bs.shader.get_value('ret')
        self.assertAlmostEqual(lum1, lum2, places=5)

    def test_lum3(self):

        code = """
ret = luminance(spec1)
        """
        col_mgr = ColorManager(spectral=True)
        rgb = col_mgr.create_spectrum((0.2, 0.3, 0.2))
        props = {'spec1':rgb, 'ret':0.0}

        bs = BasicShader(code, props, col_mgr=col_mgr)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        lum1 = col_mgr.Y(rgb)
        lum2 = bs.shader.get_value('ret')
        self.assertAlmostEqual(lum1, lum2, places=5)

if __name__ == "__main__":
    unittest.main()


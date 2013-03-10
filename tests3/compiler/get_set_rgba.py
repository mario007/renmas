import unittest

from tdasm import Runtime
from renmas3.base import ImagePRGBA
from renmas3.base import BasicShader, Vector4

class RGBATest(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_rgba(self):
        img1 = ImagePRGBA(200, 200)
        img1.set_pixel(25, 25, 0.2, 0.3, 0.4, 0.5)
        v1 = Vector4(0, 0, 0, 0)
        
        code = """
v1 = get_rgba(img, 25, 25)
        """
        props = {'img': img1, 'v1': v1}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()
        val = bs.shader.get_value('v1')
        self.assertAlmostEqual(val.x, 0.2, places=5)
        self.assertAlmostEqual(val.y, 0.3, places=5)
        self.assertAlmostEqual(val.z, 0.4, places=5)
        self.assertAlmostEqual(val.w, 0.5, places=5)

    def test_set_rgba(self):
        img1 = ImagePRGBA(200, 200)
        code = """
set_rgba(img, 25, 25, (0.1, 0.2, 0.3, 0.4))
        """
        props = {'img': img1}
        bs = BasicShader(code, props)
        runtime = Runtime()
        bs.prepare([runtime])
        #print (bs.shader._code)

        bs.execute()

        val = img1.get_pixel(25, 25)
        self.assertAlmostEqual(val[0], 0.1, places=5)
        self.assertAlmostEqual(val[1], 0.2, places=5)
        self.assertAlmostEqual(val[2], 0.3, places=5)
        self.assertAlmostEqual(val[3], 0.4, places=5)

if __name__ == "__main__":
    unittest.main()


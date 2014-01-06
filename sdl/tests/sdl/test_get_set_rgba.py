
import unittest
from tdasm import Runtime
from sdl.image import ImagePRGBA, ImageRGBA
from sdl.vector import Vector4
from sdl.shader import Shader
from sdl.args import Vec4Arg, StructArg


class GetSetRgbaTests(unittest.TestCase):

    def test_get_prgba(self):
        code = """
v1 = get_rgba(image1, 10, 10)
        """
        image = ImagePRGBA(200, 200)
        image.set_pixel(10, 10, 0.23, 0.28, 0.55, 0.8)
        p1 = StructArg('image1', image)
        p2 = Vec4Arg('v1', Vector4(0.0, 0.0, 0.0, 0.0))

        shader = Shader(code=code, args=[p1, p2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        val = shader.get_value('v1')
        self.assertAlmostEqual(val.x, 0.23)
        self.assertAlmostEqual(val.y, 0.28)
        self.assertAlmostEqual(val.z, 0.55)
        self.assertAlmostEqual(val.w, 0.8)

    def test_get_rgba(self):
        code = """
v1 = get_rgba(image1, 10, 10)
        """
        image = ImageRGBA(200, 200)
        image.set_pixel(10, 10, 25, 77, 142, 185)
        p1 = StructArg('image1', image)
        p2 = Vec4Arg('v1', Vector4(0.0, 0.0, 0.0, 0.0))

        shader = Shader(code=code, args=[p1, p2])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        val = shader.get_value('v1')
        self.assertAlmostEqual(val.x, 25 * 0.0039, places=6)
        self.assertAlmostEqual(val.y, 77 * 0.0039)
        self.assertAlmostEqual(val.z, 142 * 0.0039)
        self.assertAlmostEqual(val.w, 185 * 0.0039)

    def test_set_prgba(self):
        code = """
val = (0.67, 0.88, 0.11, 0.55)
v1 = set_rgba(image1, 10, 10, val)
        """
        image = ImagePRGBA(200, 200)
        p1 = StructArg('image1', image)
        shader = Shader(code=code, args=[p1])
        shader.compile()
        shader.prepare([Runtime()])
        shader.execute()

        r, g, b, a = image.get_pixel(10, 10)
        self.assertAlmostEqual(r, 0.67)
        self.assertAlmostEqual(g, 0.88)
        self.assertAlmostEqual(b, 0.11)
        self.assertAlmostEqual(a, 0.55)

if __name__ == "__main__":
    unittest.main()

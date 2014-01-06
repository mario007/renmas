
import unittest
from sdl.image import ImageRGBA
from sdl.blt import blt_rect, blt_image

def draw_rect(img, x, y, width, height, r, g, b, a):
    for j in range(y, y + height):
        for i in range(x, x + width):
            img.set_pixel(i, j, r, g, b, a)

class BltTest(unittest.TestCase):
    def test_blt(self):
        source = ImageRGBA(300, 200)
        dest = ImageRGBA(300, 200)
        sa, spitch = source.address_info()
        da, dpitch = dest.address_info()

        draw_rect(source, 120, 130, 10, 8, 130, 120, 150, 180)
        blt_rect(sa, 120, 130, 10, 8, spitch, da, 180, 190, dpitch, fliped=False)
        self._check_values(dest, 180, 190, 10, 8, 130, 120, 150, 180)

        blt_rect(sa, 120, 130, 10, 8, spitch, da, 50, 60, dpitch, fliped=False)
        self._check_values(dest, 50, 60, 10, 8, 130, 120, 150, 180)

    def test_blt_image(self):
        source = ImageRGBA(50, 20)
        dest = ImageRGBA(50, 20)
        draw_rect(source, 0, 0, 50, 20, 130, 120, 150, 180)
        blt_image(source, dest)
        self._check_values(dest, 0, 0, 50, 20, 130, 120, 150, 180)

    def _check_values(self, img, x, y, width, height, r, g, b, a):
        for j in range(y, y + height):
            for i in range(x, x + width):
                r2, g2, b2, a2 = img.get_pixel(i, j)

                self.assertEqual(r, r2)
                self.assertEqual(g, g2)
                self.assertEqual(b, b2)
                self.assertEqual(a, a2)

if __name__ == "__main__":
    unittest.main()


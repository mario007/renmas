
import unittest
from sdl.image import ImageRGBA

def draw_rect(img, x, y, width, height, r, g, b):
    for j in range(y, y + height):
        for i in range(x, x + width):
            img.set_pixel(i, j, r, g, b)

class ImageTest(unittest.TestCase):
    def test_img_rect(self):
        img = ImageRGBA(40, 40)
        x, y = 5, 5
        width, height = 10, 10
        r, g, b = 125, 175, 210
        draw_rect(img, x, y, width, height, r, g, b)
        for j in range(y, y + height):
            for i in range(x, x + width):
                r1, g1, b1, a1 = img.get_pixel(i, j)

                self.assertEqual(r, r1)
                self.assertEqual(g, g1)
                self.assertEqual(b, b1)

if __name__ == "__main__":
    unittest.main()

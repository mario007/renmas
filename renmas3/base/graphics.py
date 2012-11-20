
class GraphicsRGBA:
    def __init__(self):
        pass

    def draw_rect(self, img, x, y, width, height, rgb_spectrum):
        #TODO assert  BGRA
        r = int(rgb_spectrum.r * 256.0)
        g = int(rgb_spectrum.g * 256.0)
        b = int(rgb_spectrum.b * 256.0)
        for j in range(y, y + height):
            for i in range(x, x + width):
                img.set_pixel(i, j, r, g, b)

class GraphicsPRGBA:
    def __init__(self):
        pass

    def draw_rect(self, img, x, y, width, height, rgb_spectrum):
        #TODO assert  BGRA
        r = rgb_spectrum.r
        g = rgb_spectrum.g
        b = rgb_spectrum.b
        for j in range(y, y + height):
            for i in range(x, x + width):
                img.set_pixel(i, j, r, g, b)


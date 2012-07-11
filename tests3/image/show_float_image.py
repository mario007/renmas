
from renmas3.core import ImageFloatRGBA, ImageBGRA
from renmas3.utils import blt_floatbgra
from renmas3.win32 import show_image_in_window

def draw_rect(img, x, y, width, height):
    r = 0.66
    g = 0.06
    b = 0.06
    for j in range(y, y + height):
        for i in range(x, x + width):
            img.set_pixel(i, j, r, g, b)

img = ImageFloatRGBA(400, 200)

draw_rect(img, 20, 20, 100, 100)

img2 = ImageBGRA(400, 200)
blt_floatbgra(img, img2)

show_image_in_window(img2)


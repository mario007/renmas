
from renmas3.base import GraphicsPRGBA, RGBSpectrum, ImagePRGBA, ImageBGRA
from renmas3.utils import blt_floatbgra
from renmas3.win32 import show_image_in_window

img = ImagePRGBA(400, 400)
gr = GraphicsPRGBA()
gr.draw_rect(img, 20, 20, 80, 50, RGBSpectrum(0.6, 0.1, 0.1))

width, height = img.size()
img2 = ImageBGRA(width, height)
blt_floatbgra(img, img2)

show_image_in_window(img2)


from renmas3.base import GraphicsRGBA, RGBSpectrum, ImagePRGBA, ImageRGBA
from renmas3.utils import blt_prgba_to_rgba, blt_rgba_to_prgba
from renmas3.win32 import show_image_in_window

img = ImageRGBA(400, 400)
gr = GraphicsRGBA()
gr.draw_rect(img, 20, 20, 80, 50, RGBSpectrum(0.6, 0.2, 0.4))

width, height = img.size()
img2 = ImagePRGBA(width, height)
blt_rgba_to_prgba(img, img2)

img3 = ImageRGBA(width, height)
blt_prgba_to_rgba(img2, img3)

print (img.get_pixel(25,25))
print (img2.get_pixel(25,25))
print (img3.get_pixel(25,25))
show_image_in_window(img3)

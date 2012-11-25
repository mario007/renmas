
from renmas3.base import GraphicsPRGBA, RGBSpectrum, ImagePRGBA, ImageRGBA
from renmas3.utils import blt_prgba_to_rgba
from renmas3.win32 import show_image_in_window

img = ImagePRGBA(400, 400)
gr = GraphicsPRGBA()
gr.draw_rect(img, 20, 20, 80, 50, RGBSpectrum(0.6, 0.0, 0.0))

width, height = img.size()
img2 = ImageRGBA(width, height)
blt_prgba_to_rgba(img, img2)

show_image_in_window(img2)


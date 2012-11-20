
from renmas3.base import ImageRGBA, GraphicsRGBA, RGBSpectrum
from renmas3.win32 import show_image_in_window

img = ImageRGBA(400, 400)
gr = GraphicsRGBA()
gr.draw_rect(img, 20, 20, 50, 50, RGBSpectrum(0.6, 0.1, 0.1))
show_image_in_window(img)



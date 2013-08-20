import os.path
from renmas3.base import load_image, save_image
from renmas3.win32 import show_image_in_window

fname = 'lena2.ppm'
filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
print(filename)
img = load_image(filename)
print(img)

show_image_in_window(img)

fname = "lena3.ppm"
filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
save_image(filename, img)

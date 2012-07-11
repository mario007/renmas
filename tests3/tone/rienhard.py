import time
from renmas3.tone import calc_img_props_py, calc_img_props, ReinhardOperator, PhotoreceptorOperator
from renmas3.loaders import load_image
from renmas3.core import ImageBGRA
from renmas3.win32 import show_image_in_window
from renmas3.utils import blt_floatbgra

start = time.clock()
#img = load_image('Desk_oBA2.hdr')
img = load_image('AtriumNight_oA9D.hdr')
end = time.clock()
print(end-start)
print(img)
width, height = img.size()
ldr_image = ImageBGRA(width, height)
#reinhard = ReinhardOperator()
reinhard = PhotoreceptorOperator()

start = time.clock()
reinhard.tone_map(img, ldr_image)
#blt_floatbgra(img, ldr_image)
end = time.clock()
print(end-start)

show_image_in_window(ldr_image)


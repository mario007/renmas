
from renmas3.base import ImagePRGBA, ImageRGBA
from renmas3.utils import blt_prgba_to_rgba, blt_rgba_to_prgba

from renmas3.base import load_image
from renmas3.win32 import show_image_in_window
from renmas3.renderer import generate_samples

#img = load_image('Koala.jpg')
img = load_image('F:/light_probes/grace_probe.hdr')
print (img)

width, height = img.size()

samples = generate_samples(img, 100)
for sample in samples:
    pass
    #print (sample.vec)
    #print (sample.pdf)

#img2 = ImagePRGBA(width, height)
#blt_rgba_to_prgba(img, img2)

img3 = ImageRGBA(width, height)
blt_prgba_to_rgba(img, img3)

show_image_in_window(img3)

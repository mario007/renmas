
import time
from sdl import ImagePRGBA, ImageRGBA
from sdl.blt_floatrgba import blt_prgba_to_rgba
from imldr import load_image, save_image
from hdr import Tmo
from win import show_image_in_window

tm = Tmo()
tm.load('exp')

in_img = load_image('E:/hdr_images/Desk_oBA2.hdr')
w, h = in_img.size()
out_img = ImagePRGBA(w, h)

start = time.clock()
tm.tmo(in_img, out_img)
end = time.clock()
print("Tone mapping took %f\n" % (end - start))

output = ImageRGBA(w, h)
blt_prgba_to_rgba(out_img, output)

show_image_in_window(output, fliped=True)

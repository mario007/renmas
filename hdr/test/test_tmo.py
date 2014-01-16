
from sdl import ImagePRGBA
from imldr import load_image
from hdr import Tmo

tm = Tmo()
tm.load('exp')

in_img = load_image('E:/hdr_images/Desk_oBA2.hdr')
w, h = in_img.size()
out_img = ImagePRGBA(w, h)

tm.tmo(in_img, out_img)

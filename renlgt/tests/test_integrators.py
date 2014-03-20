
from sdl.blt_floatrgba import blt_prgba_to_rgba, ImageRGBA
from imldr import save_image
from renlgt import Renderer

ren = Renderer()
#ren.load('sphere1.txt')
ren.load('triangle1.txt')
ren.prepare()

ren.render()
ren.tmo()

width, height = ren._hdr_buffer.size()
new_img = ImageRGBA(width, height)
#blt_prgba_to_rgba(ren._hdr_buffer, new_img)
blt_prgba_to_rgba(ren._hdr_output, new_img)

save_image("render1.jpeg", new_img)



import winlib
import math
from renmas.gui import MainWindow, Blitter, ImageRGBA, ImageFloatRGBA
from tdasm import Tdasm, Runtime
from renmas.core import Rng
import random

runtime = Runtime()

Rng.random_int(runtime, "randint")
Rng.random_float(runtime, "randfloat")

test_asm = """
    #DATA
    uint32 rnd_n[4]
    float rnd[4]


    #CODE

    call randint
    ;call randfloat
    

    vmovdqa oword [rnd_n], xmm0
    ;vmovaps oword [rnd], xmm0

    #END
"""

asm = Tdasm()
mc = asm.assemble(test_asm)
ds = runtime.load("test", mc)

img = ImageRGBA(400, 400)
img_addr, img_pitch = img.get_addr()
width, height = img.get_size()

img2 = ImageRGBA(400, 400)
img2_addr, img2_pitch = img2.get_addr()
width2, height2 = img2.get_size()

a = 1.0 / 4294967295.0

print(height)
for x in range(width):
    img.set_pixel(x, 0, 0, 0, 255)
    img.set_pixel(x, height-1, 0, 0, 255)
    img2.set_pixel(x, 0, 0, 0, 255)
    img2.set_pixel(x, height-1, 0, 0, 255)

for y in range(0, height, 40):
    for x in range(width):
        img.set_pixel(x, y, 0, 0, 255)
        img2.set_pixel(x, y, 0, 0, 255)

for x in range(0, width, 40):
    for y in range(height):
        img.set_pixel(x, y, 0, 0, 255)
        img2.set_pixel(x, y, 0, 0, 255)

for y in range(height):
    img.set_pixel(0, y, 0, 0, 255)
    img.set_pixel(width-1, y, 0, 0, 255)
    img2.set_pixel(0, y, 0, 0, 255)
    img2.set_pixel(width-1, y, 0, 0, 255)


for x in range(128):
    runtime.run("test")
    n = ds["rnd_n"]
    x1 = n[0] * a
    y1 = n[1] * a
    x2 = n[2] * a
    y2 = n[3] * a
    #print(x1, y1, x2, y2)

    #x1 = n[0] 
    #y1 = n[1] 
    #x2 = n[2] 
    #y2 = n[3] 
    
    x1 = int(x1 * width)
    y1 = int(y1 * height)
    x2 = int(x2 * width)
    y2 = int(y2 * width)
    #print(x1, y1, x2, y2)
    x3 = int(random.random() * width)
    y3 = int(random.random() * height)
    x4 = int(random.random() * width)
    y4 = int(random.random() * width)

    img.set_pixel(x1, y1, 0, 255, 255)
    img.set_pixel(x2, y2, 0, 255, 255)
    img2.set_pixel(x3, y3, 0, 255, 255)
    img2.set_pixel(x4, y4, 0, 255, 255)

win = MainWindow(1200, 600, "Test")
addr, spitch = win.get_addr()

blitter = Blitter()
blitter.blt_rgba(addr, 100, 100, 500, 500, spitch, img_addr, 0, 0, width, height, img_pitch)

blitter.blt_rgba(addr, 600, 100, 1000, 500, spitch, img2_addr, 0, 0, width2, height2, img2_pitch)
win.redraw()
winlib.MainLoop()
print(4) 


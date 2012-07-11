
import time
import random
import winlib
import renmas2
import renmas2.core
import renmas2.tone_mapping

blitter = renmas2.core.Blitter()
def blt_float_img_to_window(x, y, img2, img):
    da, dpitch = img2.get_addr()
    dw, dh = img2.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

def blt_image(x, y, img1, img2):
    da, dpitch = img1.get_addr()
    dw, dh = img1.get_addr()
    sa, spitch = img2.get_addr()
    sw, sh = img2.get_size()
    blitter.blt_rgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)


start = time.clock()
#hdr_image = renmas2.core.load_rgbe("E:/hdr_images/Desk_oBA2.hdr")
hdr_image = renmas2.core.load_rgbe("E:/hdr_images/AtriumNight_oA9D.hdr")
end = time.clock() - start
print("Time to load picture:", end)
print(hdr_image)

ldr_image = renmas2.core.ImageRGBA(hdr_image.width, hdr_image.height)
tone_mapper = renmas2.tone_mapping.PhotoreceptorOperator()
#tone_mapper = renmas2.tone_mapping.ReinhardOperator()
tone_mapper.tone_map(ldr_image, hdr_image, 0, 0, ldr_image.width, ldr_image.height)
print (ldr_image.width, ldr_image.height)

win = renmas2.core.MainWindow(600, 400, "Test")

#blt_float_img_to_window(0, 0, ldr_image, hdr_image)
blt_image(0, 0, win, ldr_image)
win.redraw()
winlib.MainLoop()


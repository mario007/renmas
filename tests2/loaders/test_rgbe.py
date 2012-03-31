import time
import random
import winlib
import renmas2
import renmas2.core

blitter = renmas2.core.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

start = time.clock()
image = renmas2.core.load_rgbe("I:/hdr_images/Desk_oBA2.hdr")
#ret = renmas2.core.load_rgbe("I:/hdr_images/Apartment_float_o15C.hdr")
end = time.clock() - start
print("Time to load picture:", end)
print(image)

win = renmas2.core.MainWindow(600, 400, "Test")
blt_float_img_to_window(0, 0, image, win)
win.redraw()
winlib.MainLoop()


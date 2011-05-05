
import winlib
import renmas.gui 
import timeit

def create_rgba_image():
    img = renmas.gui.ImageRGBA(100, 100)
    for y in range(75):
        for x in range(50):
            img.set_pixel(x, y, 0, 0, 255) #blue
    return img

def create_float_image():
    img = renmas.gui.ImageFloatRGBA(400, 300)
    for y in range(75):
        for x in range(25):
            img.set_pixel(x, y, 0.99, 0, 0) #red
    return img
    
def blt_img_to_window(x, y, blitter, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_rgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

def blt_float_img_to_window(x, y, blitter, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

win = renmas.gui.MainWindow(500, 500, "Test")

blitter = renmas.gui.Blitter()
img = create_rgba_image()
blt_img_to_window(80, 50, blitter, img, win)

img_float = create_float_image()

def blt():
    blt_float_img_to_window(350, 100, blitter, img_float, win)

t = timeit.Timer(lambda : blt())
print ("time", t.timeit(1))


win.redraw()
winlib.MainLoop()

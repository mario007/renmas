
import winlib
import renmas.gui 

def blt_img_to_window(x, y, blitter, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_rgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

win = renmas.gui.MainWindow(500, 500, "Test")

blitter = renmas.gui.Blitter()
img = renmas.gui.load_image("Koala.jpg")
blt_img_to_window(10, 10, blitter, img, win)

# for now just png is supported.
renmas.gui.save_image("Novakoala.png", img)

win.redraw()
winlib.MainLoop()


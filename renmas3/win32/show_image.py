
from renmas3.base import ImageRGBA, ImageBGRA
from .window import Window, main_loop
from renmas3.utils import blt_rect

#TODO -- window buffer is big in dimension of destkop window
# so if image is bigger than this it will craches
# WindowsGDI wants that pixels are in bgra format!!!. 
def show_image_in_window(image, fname=None):

    if fname is None: fname = "UnknownImage"
    if isinstance(image, ImageRGBA):
        image = image.to_bgra()
    assert isinstance(image, ImageBGRA)

    width, height = image.size()
    win = Window(width+20,  height+20, fname)
    
    da, dpitch = win.address_info()
    sa, spitch = image.address_info()
    blt_rect(sa, 0, 0, width, height, spitch, da, 0, 0, dpitch, fliped=True)

    win.redraw()
    main_loop()


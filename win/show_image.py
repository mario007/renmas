
from sdl.image import ImageRGBA, ImageBGRA
from sdl.blt import blt_rect
from .window import Window, main_loop

#TODO -- window frame buffer is 2560x1600. Improve this.
# Note. WindowsGDI wants that pixels are in bgra format!!!. 
def show_image_in_window(image, title=None, fliped=False):
    """
        Create window and show image.
        @param image - image to show
        @param title - text that will be shown in title bar of window 
        @param fliped - flip image vertical
    """

    if title is None:
        title = "UnknownImage"
    if isinstance(image, ImageRGBA):
        image = image.to_bgra()
    assert isinstance(image, ImageBGRA)

    width, height = image.size()
    win = Window(width+20,  height+20, title)
    
    da, dpitch = win.address_info()
    sa, spitch = image.address_info()
    blt_rect(sa, 0, 0, width, height, spitch, da, 0, 0, dpitch, fliped)

    win.redraw()
    main_loop()


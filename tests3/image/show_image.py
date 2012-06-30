import argparse 
from renmas3.win32 import Window, main_loop
from renmas3.loaders import load_image
from renmas3.utils import blt_rect
from renmas3.core import ImageRGBA, ImageBGRA

def _show_image(image, fname=None):

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    args = parser.parse_args()
    img = load_image(args.fname)
    if img is not None:
        _show_image(img, args.fname)
    else:
        print("Image %s could not be loaded!" % args.fname)

if __name__ == "__main__":
    main()


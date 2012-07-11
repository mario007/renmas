
import argparse 

from renmas3.core import ImageFloatRGBA, ImageBGRA
from renmas3.win32 import show_image_in_window
from renmas3.loaders import load_image
from renmas3.tone import PhotoreceptorOperator

def show_hdr_image(hdr_image, m=0.6, c=0.5, a=0.5, f=1.0, fname=None):
    reinhard = PhotoreceptorOperator(m, c, a, f)
    width, height = hdr_image.size()
    ldr_image = ImageBGRA(width, height)
    reinhard.tone_map(hdr_image, ldr_image)
    show_image_in_window(ldr_image, fname)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', help='Name of the file')
    parser.add_argument('-m', help='Contrast. Input Range: 0-1')
    parser.add_argument('-c', help='Adaptation. Input Values:0-1')
    parser.add_argument('-a', help='Colornes. Input Values:0-1')
    parser.add_argument('-f', help='Lightnes.')
    args = parser.parse_args()
    
    m = 0.6
    if args.m:
        m = float(args.m)
    c = 0.5
    if args.c:
        c = float(args.c)
    a = 0.5
    if args.a:
        a = float(args.a)
    f = 1.0 
    if args.f:
        f = float(args.f)

    img = load_image(args.fname)
    if img is not None:
        if isinstance(img, ImageFloatRGBA):
            show_hdr_image(img, m, c, a, f, fname=args.fname)
        else:
            print("Image %s is not hdr image!" % args.fname)
    else:
        print("Image %s could not be loaded!" % args.fname)


if __name__ == "__main__":
    main()


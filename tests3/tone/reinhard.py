
import argparse 

from renmas3.core import ImageFloatRGBA, ImageBGRA
from renmas3.win32 import show_image_in_window
from renmas3.loaders import load_image
from renmas3.tone import ReinhardOperator

def show_hdr_image(hdr_image, key=0.18, saturation=0.6, fname=None):
    reinhard = ReinhardOperator(key, saturation)
    width, height = hdr_image.size()
    ldr_image = ImageBGRA(width, height)
    reinhard.tone_map(hdr_image, ldr_image)
    show_image_in_window(ldr_image, fname)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', help='Name of the file')
    parser.add_argument('-key', help='Scene key that is used in tone mapping.')
    parser.add_argument('-saturation', help='Saturation. Input Values:0-1')
    args = parser.parse_args()
   
    key = 0.18
    saturation = 0.6
    if args.key:
        key = float(args.key)
    if args.saturation:
        saturation = float(saturation)

    img = load_image(args.fname)
    if img is not None:
        if isinstance(img, ImageFloatRGBA):
            show_hdr_image(img, key, saturation, fname=args.fname)
        else:
            print("Image %s is not hdr image!" % args.fname)
    else:
        print("Image %s could not be loaded!" % args.fname)


if __name__ == "__main__":
    main()

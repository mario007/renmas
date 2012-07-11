import argparse 

from renmas3.win32 import show_image_in_window
from renmas3.loaders import load_image, save_image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    args = parser.parse_args()
    img = load_image(args.fname)
    if img is not None:
        show_image_in_window(img, args.fname)
    else:
        print("Image %s could not be loaded!" % args.fname)

if __name__ == "__main__":
    main()


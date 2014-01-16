
from sdl.image import ImagePRGBA, ImageRGBA, ImageBGRA
from sdl.blt_floatrgba import blt_prgba_to_bgra, blt_prgba_to_rgba
from imldr import load_image, save_image


def create_image(objects, args):
    pix_format, width, height = args.split(',')
    if pix_format == 'RGBA':
        img = ImageRGBA(int(width), int(height))
    elif pix_format == 'BGRA':
        img = ImageBGRA(int(width), int(height))
    elif pix_format == 'PRGBA':
        img = ImagePRGBA(int(width), int(height))
    else:
        raise ValueError("Unknown pixel format", pix_format)

    objects[str(id(img))] = img
    return str(id(img))


def convert_to_bgra(objects, args):
    id_obj = args
    if id_obj not in objects:
        raise ValueError("Image doesn't exist in objects! Id = %s" % id_obj)
    img = objects[id_obj]
    width, height = img.size()
    if isinstance(img, ImageRGBA):
        new_img = img.to_bgra()
    elif isinstance(img, ImageBGRA):
        tmp_img = img.to_rgba()
        new_img = tmp_img.to_bgra()
    elif isinstance(img, ImagePRGBA):
        new_img = ImageBGRA(width, height)
        blt_prgba_to_bgra(img, new_img)

    objects[str(id(new_img))] = new_img
    return str(id(new_img))


def load_hdr_image(objects, args):
    fname = args
    img = load_image(fname)
    if img is None:
        raise ValueError("Could not load %s image." % fname)

    if not isinstance(img, ImagePRGBA):
        raise ValueError("Loaded %s image is not hdr image!" % fname)

    objects[str(id(img))] = img
    return str(id(img))


def save_image(objects, args):
    fname, id_img = args.split(',')
    image = objects[id_img]
    if isinstance(image, ImagePRGBA):
        width, height = image.size()
        new_img = ImageRGBA(width, height)
        blt_prgba_to_rgba(image, new_img)
        save_image(fname, new_img)
    elif isinstance(image, ImageRGBA):
        save_image(fname, image)
    elif isinstance(image, ImageBGRA):
        new_img = image.to_rgba()
        save_image(fname, new_img)
    return ""


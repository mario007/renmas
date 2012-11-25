
import platform
import os.path

from .image import ImageBGRA
from .tga import save_tga

_image_writers = {
        'tga': save_tga
        }

def register_image_writer(typ, func):
    _image_writers[typ] = func

def save_image(fname, image, typ=None):
    if isinstance(image, ImageBGRA):
        image = image.to_rgba()

    if typ is not None:
        if typ in _image_writers:
            return _image_writers[typ](fname, image)

    name, ext = os.path.splitext(fname)
    if ext == "":
        return save_tga(fname, image)
    ext = ext[1:] # Remove period from extension 
    if ext in _image_writers:
        return _image_writers[ext](fname, image)

    return save_tga(fname, image)


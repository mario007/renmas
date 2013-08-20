
import platform
import os.path

from .image import ImageBGRA
from .tga import save_tga
from .ppm import save_ppm

# extension in C++ that uses GDI+ to load image
def _windows_image_save(fname):
    try:
        import imload
        width, height = imload.QueryImage(fname)
        im = ImageRGBA(width, height)
        addr, pitch = im.address_info()
        imload.GetImage(fname, addr, width, height)
        return im
    except ImportError:
        return None

    return None

def save_png(fname, image):
    try:
        import imload
    except ImportError:
        return False
    addr, pitch = image.address_info()
    width, height = image.size()
    imload.SaveRGBAToPNG(fname, addr, width, height)
    return True
    

_image_writers = {
        'tga': save_tga,
        'png': save_png,
        'ppm': save_ppm
        }

def register_image_writer(typ, func):
    _image_writers[typ] = func

def save_image(fname, image, typ=None):
    #TODO hdr support
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

    fname = fname + '.tga'
    return save_tga(fname, image)


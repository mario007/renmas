import platform
import os.path

from sdl.image import ImageRGBA, ImagePRGBA
from .tga import load_tga
from .rgbe import load_hdr
from .ppm import load_ppm

# extension in C++ uses GDI+ to load image
def _windows_image_loader(fname):
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

def load_png(fname):
    if platform.system() == "Windows":
        return _windows_image_loader(fname)
    else:
        return None # #TODO implement linux png loader
    
def load_jpg(fname):
    if platform.system() == "Windows":
        return _windows_image_loader(fname)
    else:
        return None # #TODO implement linux jpg loader

_image_loaders = {
        'png': load_png,
        'tga': load_tga,
        'jpg': load_jpg,
        'hdr': load_hdr,
        'ppm': load_ppm
        }

def register_image_loader(typ, func):
    _image_loaders[typ] = func

# Return type of the image
def _detect_format(fname):
    name, ext = os.path.splitext(fname)
    if ext == "":
        pass #TODO -- load first couple of bytes and try to detect type of file
        return None
    else:
        return ext[1:] #Remove period from extension


def _load_image_frimgldr(fname):
    import freeimgldr
    width, height, bpp = freeimgldr.QueryImage(fname)
    if bpp > 32:
        im = ImagePRGBA(width, height)
    else:
        im = ImageRGBA(width, height)
    addr, pitch = im.address_info()
    freeimgldr.GetImage(fname, addr, width, height, bpp)
    return im


def load_image(fname):
    """
        Load image form disk. Function use FreeImage library to load
        image from disk. If the FreeImage library is not present, it
        uses own built-in loaders for loading images but number of
        supported formats is reduced.

        arguments:
        fname - file name (abosulte or relative to the current working directory)

    """

    if not os.path.isfile(fname):
        raise FileNotFoundError(fname)

    try:
        import freeimgldr
        return _load_image_frimgldr(fname)
    except ImportError:
        pass

    typ = _detect_format(fname)
    if typ is None:
        return None #unknown type of image file
    typ = typ.lower()
    if typ in _image_loaders:
        return _image_loaders[typ](fname)

    return None #we don't have loader for requested type of image file


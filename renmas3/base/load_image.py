import platform
import os.path

from .image import ImageRGBA
from .tga import load_tga
from .rgbe import load_hdr

# extension in C++ that uses GDI+ to load image
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
        'hdr': load_hdr
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

def load_image(fname):

    if not os.path.isfile(fname):
        return None #file doesn't exists

    typ = _detect_format(fname)
    if typ is None:
        return None #unknown type of image file
    if typ in _image_loaders:
        return _image_loaders[typ](fname)

    return None #we don't have loader for requested type of image file


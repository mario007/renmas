import platform
import os.path

from .tga import load_tga

def windows_png_loader(fname):
    try:
        import imload # extension in C++ that uses GDI+ to load image
    except ImportError:
        return None

    return None

def load_png(fname):
    if platform.system() == "Windows":
        return windows_png_loader(fname)
    else:
        return None # #TODO implement linux png loader
    

_image_loaders = {
        'png': load_png,
        'tga': load_tga
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

    if not os.path.isfile(fname): return None #file doesn't exists

    typ = _detect_format(fname)
    if typ is None: return None #unknown type of image file
    if typ in _image_loaders:
        return _image_loaders[typ](fname)

    return None #we don't have loader for requested type of image file


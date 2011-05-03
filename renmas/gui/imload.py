
import os
import imload
from .image import ImageRGBA

def load_image(name):
    if os.path.isfile(name):
        width, height = imload.QueryImage(name)
        im = ImageRGBA(width, height)
        addr, pitch = im.get_addr()
        imload.GetImage(name, addr, width, height)
        return im
    return None

def save_image(name, img): #png for know! TODO implement others FIXME - pitch
    addr, pitch = img.get_addr()
    width, height = img.get_size()
    imload.SaveRGBAToPNG(name, addr, width, height)



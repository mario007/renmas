
import os
import imload
from .image import ImageRGBA

class ImageLoader:
    def __init__(self):
        pass

    def load(self, name):
        if os.path.isfile(name):
            width, height = imload.QueryImage(name)
            im = ImageRGBA(width, height)
            addr, pitch = im.get_addr()
            imload.GetImage(name, addr, width, height)
            return im
        return None



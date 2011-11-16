import math
from tdasm import Runtime
from ..macros import macro_call, assembler


class Sampler:
    def __init__(self, width, height, spp=1, pixel_size=1.0):
        self._width = width
        self._height = height
        self._pixel_size = float(pixel_size)
        self._spp = int(spp)

    def resolution(self, width, height):
        self._width = width
        self._height = height

    def get_sample(self):
        raise NotImplementedError()

    def get_sample_asm(self, runtimes, label):
        raise NotImplementedError()

    def _update_ds(self):
        raise NotImplementedError()
        
    def set_tile(self, tile):
        self._tile = tile
        self._curx = tile.x 
        self._cury = tile.y
        self._update_ds()

    def set_pixel_size(self, pixel_size):
        self._pixel_size = float(pixel_size)

    def get_pixel_size(self):
        return self._pixel_size

    def spp(self, spp):
        self._spp = int(spp) 


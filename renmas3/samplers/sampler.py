import math
from tdasm import Runtime

class Sampler:
    def __init__(self, width, height, spp=1, pixel_size=1.0):
        self._width = width
        self._height = height
        self._pixel_size = float(pixel_size)
        self._spp = int(spp)

    def set_resolution(self, width, height):
        self._width = width
        self._height = height

    def get_sample(self):
        raise NotImplementedError()

    def get_sample_asm(self, runtimes, label, assembler):
        raise NotImplementedError()

    def set_tile(self, tile):
        raise NotImplementedError()

    def set_pixel_size(self, pixel_size):
        self._pixel_size = float(pixel_size)

    def get_pixel_size(self):
        return self._pixel_size

    def set_spp(self, spp):
        s = int(spp)
        if s < 1: self._spp = 1
        else: self._spp = s

    def get_spp(self):
        return self._spp


import math
from tdasm import Runtime
from ..base import arg_map, arg_list, Float, Integer, BaseShader, Tile2D
from .sample import Sample

class Sampler(BaseShader):
    """Base class for samplers."""

    def __init__(self, width, height, code, nsamples=1, pixel_size=1.0):
        super(Sampler, self).__init__(code)
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self._tile = Tile2D(0, 0, width, height)
        self.set_spp(nsamples)

    def set_resolution(self, width, height):
        self.width = width
        self.height = height

    def set_spp(self, nsamples):
        self._spp = int(nsamples)

    def has_more_samples(self, n):
        if n >= self._spp:
            return False
        return True

    def set_pass(self, n):
        self._curx = self._tile.x
        self._cury = self._tile.y
        self._endx = self._tile.x + self._tile.width
        self._endy = self._tile.y + self._tile.height
        self.update()

    def get_props(self, nthreads):
        props = {}
        props['width'] = self.width
        props['height'] = self.height
        props['pixel_size'] = self.pixel_size
        props['spp'] = self._spp
        if nthreads == 1:
            props['tile'] = self._tile
            props['curx'] = self._tile.x
            props['cury'] = self._tile.y
            props['endx'] = self._tile.x + self._tile.width 
            props['endy'] = self._tile.y + self._tile.height
            return props

        arr_props = []
        self._tile.split(nthreads)
        for tile in self._tile.tiles:
            d = props.copy()
            d['tile'] = tile
            d['curx'] = tile.x
            d['cury'] = tile.y
            d['endx'] = tile.x + tile.width 
            d['endy'] = tile.y + tile.height
            arr_props.append(d)
        return arr_props

    def arg_map(self):
        args = arg_map([('tile', Tile2D), ('width', Integer),
                        ('height', Integer), ('pixel_size', Float),
                        ('spp', Integer), ('curx', Integer), ('cury', Integer),
                        ('endx', Integer), ('endy', Integer)])

        return args

    def arg_list(self):
        return arg_list([('sample', Sample)])

    def method_name(self):
        return 'generate_sample'

    def standalone(self):
        return False

    def generate_sample(self):
        raise NotImplementedError()

# xw = pixel_size(x - width/2 + 0.5)
# yw = pixel_size(y - height/2 + 0.5)
#return Sample_(xw, yw, self._curx, self._cury, 1.0)

class RegularSampler(Sampler):
    def __init__(self, width, height, pixel_size=1.0):
        code = self.shader_code()
        super(RegularSampler, self).__init__(width, height,
                                             code, 1, pixel_size)

    def set_spp(self, nsamples):
        self._spp = 1

    def shader_code(self):
        code = """
if cury == endy:
    return 0

tmp = curx - width * 0.5
tmp2 = cury - height * 0.5

sample.x = pixel_size * (tmp + 0.5)
sample.y = pixel_size * (tmp2 + 0.5)
sample.ix = curx
sample.iy = cury
sample.weight = 1.0

curx = curx + 1
if curx == endx:
    curx = tile.x
    cury = cury + 1
return 1

        """
        return code

    def generate_sample(self):

        if self._cury == self._endy:
            return None

        #x = (self._curx - self.width * 0.5 + 0.5)
        #y = (self._cury - self.height * 0.5 + 0.5)
        x = self.pixel_size * (self._curx - self.width * 0.5 + 0.5)
        y = self.pixel_size * (self._cury - self.height * 0.5 + 0.5)
        sample = Sample(x, y, self._curx, self._cury, 1.0)

        self._curx += 1
        if self._curx == self._endx:
            self._curx = self._tile.x
            self._cury += 1
        return sample


class Sampler_old:
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


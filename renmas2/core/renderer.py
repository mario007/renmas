
import math
from tdasm import Runtime
from ..samplers import RandomSampler, RegularSampler
from ..integrators import Raycast
from .tile import Tile

class Renderer:
    def __init__(self):
        self._ready = False

        #default values for renderer
        self._width =  1000 
        self._height = 1000 
        self._spp = 2 
        self._algorithm = Raycast(self)
        #self._sampler = RegularSampler(self._width, self._height)
        self._sampler = RandomSampler(self._width, self._height, spp=self._spp)
        self._threads = 1
        self._max_samples = 100000 #max samples in tile

    def resolution(self, width, height):
        self._width = width
        self._height = height

    def set_samplers(self, sampler): #Tip: First solve for one sampler
        pass

    def get_samplers(self):
        pass

    def _get_sampler(self):
        return self._sampler

    def threads(self, n):
        nc = abs(int(n))
        if nc > 32: nc = 32 #max number of threads
        self._threads = nc

    def prepare(self): #build acceleration structures 
        self.reset()
        self._create_runtimes()
        self._ready = True

    def _create_runtimes(self):
        self._runtimes = [Runtime() for n in range(self._threads)] 
        self._sampler.get_sample_asm(self._runtimes, 'get_sample')

        self._algorithm.algorithm_asm(self._runtimes)

    def set_algorithm(self, name, asm=False):
        pass

    def get_algorithm():
        pass

    def add(name, obj): #add material, shape, light etc...
        pass

    def render(self):
        if not self._ready: self.prepare()
        if not self._ready: return None #unexpected error ocur!!!! TODO
        try:
            tile = self._tiles.pop()
        except IndexError:
            return False # All tiles are rendererd

        self._algorithm.render(tile)
        return True

    def reset(self):
        self._create_tiles()

    def _create_tiles(self):

        width = self._width
        height = self._height

        w = h = int(math.sqrt(self._max_samples / self._spp))
        #w = h = 50
        sx = sy = 0
        xcoords = []
        ycoords = []
        tiles = []
        while sx < width:
            xcoords.append(sx)
            sx += w
        last_w = width - (sx - w) 
        while sy < height:
            ycoords.append(sy)
            sy += h
        last_h = height - (sy - h)

        for i in xcoords:
            for j in ycoords:
                tw = w
                th = h
                if i == xcoords[-1]:
                    tw = last_w
                if j == ycoords[-1]:
                    th = last_h
                t = Tile(i, j, tw, th)
                t.split(self._threads) #multithreading
                tiles.append(t)

        self._tiles = tiles


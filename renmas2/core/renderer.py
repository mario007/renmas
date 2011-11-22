
import math
from tdasm import Runtime
from ..samplers import RandomSampler, RegularSampler
from ..cameras import Pinhole
from ..integrators import Raycast, IsectIntegrator
from .intersector import Intersector
from .film import Film
from .tile import Tile

class Renderer:
    def __init__(self):
        self._ready = False

        #default values for renderer
        self._width =  400 
        self._height = 400 
        self._spp = 4 
        self._intersector = Intersector()
        self._integrator = IsectIntegrator(self)
        #self._sampler = RegularSampler(self._width, self._height)
        self._sampler = RandomSampler(self._width, self._height, spp=self._spp)
        self._film = Film(self._width, self._height, self._spp)
        self._camera = Pinhole((10,10,10), (0,0,0), 1600)
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
        self._intersector.prepare()
        self._integrator.prepare()
        self._film.reset()
        self._ready = True

    def _create_runtimes(self):
        self._runtimes = [Runtime() for n in range(self._threads)] 
        self._sampler.get_sample_asm(self._runtimes, 'get_sample')
        self._camera.ray_asm(self._runtimes, 'get_ray')

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

        self._integrator.render(tile)
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


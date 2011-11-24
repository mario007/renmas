
from tdasm import Runtime
from ..samplers import RandomSampler, RegularSampler
from ..cameras import Pinhole
from ..integrators import Raycast, IsectIntegrator
from ..shapes import Shape
from .intersector import Intersector
from .film import Film
from .methods import create_tiles

class Renderer:
    def __init__(self):
        self._ready = False

        self._default_values()

        self._intersector = Intersector()
        self._integrator = IsectIntegrator(self)
        #self._sampler = RegularSampler(self._width, self._height)
        self._sampler = RandomSampler(self._width, self._height, spp=self._spp)
        self._spp = self._sampler._spp
        self._film = Film(self._width, self._height, self._spp)
        self._camera = Pinhole(self._eye, self._lookat, self._distance)

    def _default_values(self):
        self._width =  200 
        self._height = 200 
        self._spp = 1 
        self._threads = 1
        self._max_samples = 10000000 #max samples in tile
        self._eye = (10, 10, 10)
        self._lookat = (0, 0, 0)
        self._distance = 400

    def resolution(self, width, height):
        self._width = width
        self._height = height
        self._film.set_resolution(width, height)
        self._sampler.set_resolution(width, height)

    def spp(self, n):
        self._sampler.spp(n)
        self._spp = self._sampler._spp 
        self._film.set_nsamples(self._spp)

    def set_samplers(self, samplers): #Tip: First solve for one sampler
        self._sampler = samplers[0]
        self._samplers = samplers
        self._ready = False

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

    def reset(self):
        self._tiles = create_tiles(self._width, self._height, self._spp, self._max_samples, self._threads)
        self._tiles2 = list(self._tiles)

    def camera_moved(self, edx, edy, edz, ldx, ldy, ldz):#regulation of distance is missing for now
        self._tiles = list(self._tiles2)
        self._camera.camera_moved(edx, edy, edz, ldx, ldy, ldz)

    def set_integrator(self, name):
        self._ready = False

    def set_camera(self, camera):
        self._camera = camera 
        self._ready = False

    def add(self, name, obj): #add material, shape, light etc...
        if isinstance(obj, Shape):
            self._intersector.add(name, obj)
        else:
            raise ValueError("Unknown type of object!") #TODO log not exception !!! exception is just for testing
        self._ready = False

    def render(self):
        if not self._ready: self.prepare()
        if not self._ready: return None #unexpected error ocur!!!! TODO
        try:
            tile = self._tiles.pop()
        except IndexError:
            return False # All tiles are rendererd

        self._integrator.render(tile)
        return True


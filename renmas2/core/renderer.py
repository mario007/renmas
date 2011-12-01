
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
        self._max_samples = 100000 #max samples in tile
        self._eye = (10, 10, 10)
        self._lookat = (0, 0, 0)
        self._distance = 400
        self._pixel_size = 1.0

    def asm(self, flag):
        self._asm = bool(flag)
        self._integrator.asm(flag)
        if self._asm: self._max_samples = 10000000
        else: self._max_samples = 100000
        self._ready = False

    def resolution(self, width, height):
        width = self._int(self._width, width)
        height = self._int(self._height, height)
        self._width = width
        self._height = height
        self._film.set_resolution(width, height)
        self._sampler.set_resolution(width, height)

    def spp(self, n):
        n = self._int(self._spp, n)
        self._sampler.spp(n)
        self._spp = self._sampler._spp 
        self._film.set_nsamples(self._spp)

    def set_pixel_size(self, size):
        size = self._float(self._pixel_size, size)
        self._pixel_size = size
        self._sampler.set_pixel_size(self._pixel_size)

    def blt_frame_buffer(self):
        self._film.blt_image_to_buffer()
        
    def set_samplers(self, samplers): #Tip: First solve for one sampler
        self._sampler = samplers[0]
        self._samplers = samplers
        self._ready = False

    def threads(self, n):
        n = self._int(self._threads, n)
        nc = abs(n)
        if nc > 32: nc = 32 #max number of threads
        self._threads = nc
        self._ready = False

    def prepare(self): #prepare everything that is needed for rendering 
        self._tiles = create_tiles(self._width, self._height, self._spp, self._max_samples, self._threads)
        self._tiles2 = create_tiles(self._width, self._height, self._spp, self._max_samples, self._threads)
        self._intersector.prepare()
        self._integrator.prepare()
        self._film.reset()
        self._ready = True

    def reset(self): #restart of rendering
        self._tiles = list(self._tiles2)
        #TODO -- wipe- erase back baffer!!!!

    def camera_moved(self, edx, edy, edz, ldx, ldy, ldz):#regulation of distance is missing for now - TODO - test this
        self._tiles = list(self._tiles2)
        self._camera.camera_moved(edx, edy, edz, ldx, ldy, ldz)

    def set_integrator(self, integrator):
        self._integrator = integrator 
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

    def _float(self, old, new):
        try:
            return float(new)
        except:
            return old 

    def _int(self, old, new):
        try:
            return int(new)
        except:
            return old


import time

from .col_mgr import ColorManager
from .logger import log
from .shape_mgr import ShapeManager
from .film import Film
from ..cameras import Pinhole
from ..samplers import RandomSampler, RegularSampler
from .tile import create_tiles 
from ..integrators import IsectIntegrator
from ..shapes import Shape
from .image import ImageBGRA, ImageFloatRGBA
from ..tone import ReinhardOperator, PhotoreceptorOperator 
from ..utils import blt_floatbgra

class Renderer:
    def __init__(self):

        self._ready = False
        self._default_values()
        self._default_objects()

    def _default_values(self):
        self._width =  300 
        self._height = 300 
        self._spp = 1 
        self._threads = 1 
        self._max_samples = 100000 #max samples in tile
        self._pixel_size = 1.0
        self._default_material = "default" #name of default material
        self._asm = True 
        self._tone_mapping = True 
        self._current_pass = 0

    def _default_objects(self):
        self._color_manager = ColorManager()
        self._camera = Pinhole(eye=(0,0,10), lookat=(0,0,0), distance=400)
        self._sampler = RegularSampler(self._width, self._height)
        #self._sampler = RandomSampler(self._width, self._height, spp=self._spp)
        self._shp_mgr = ShapeManager(self)
        self._film = Film(self._width, self._height, self)
        self._integrator = IsectIntegrator(self)
        self._image = ImageBGRA(self._width, self._height)
        self._tone_op = ReinhardOperator()

    @property
    def macro_call(self):
        return self._color_manager.macro_call

    @property
    def assembler(self):
        return self._color_manager.assembler

    @property
    def color_mgr(self):
        return self._color_manager

    @property
    def sampler(self):
        return self._sampler

    @property
    def camera(self):
        return self._camera

    @property
    def shape_mgr(self):
        return self._shp_mgr

    @property
    def film(self):
        return self._film

    def _set_asm(self, value):
        self._asm = bool(value)
        if self._asm:
            self._max_samples = 200000 
        else:
            self._max_samples = 10000
        self._ready = False

    def _get_asm(self):
        return self._asm

    asm = property(_get_asm, _set_asm)

    def _set_threads(self, value):
        nc = abs(int(value))
        if nc > 32: nc = 32 #max number of threads
        self._threads = nc
        self._ready = False

    def _get_threads(self):
        return self._threads

    threads = property(_get_threads, _set_threads)

    def prepare(self): #prepare everything that is needed for rendering 
        start = time.clock()
        self._tiles = create_tiles(self._width, self._height, 1, self._max_samples, self._threads)
        self._shp_mgr.prepare()
        self._integrator.prepare()
        self._current_pass = 0
        self._ready = True
        end = time.clock()
        log.info("Time that took to prepare renderer for rendering: " + str(end-start) + " seconds.")

    def render(self):
        if not self._ready:
            self.prepare()
        if not self._ready:
            return None #unexpected error ocur!!!! TODO
        self._film.set_pass(self._current_pass) #required for assembly rendering
        for tile in self._tiles:
            self._integrator.render(tile)

        self._current_pass += 1
        if self._current_pass >= self._spp:
            return False
        else:
            return True

    def tone_map(self): #tone mapping of whole image
        if self._tone_mapping: 
            self._tone_op.tone_map(self._film.image, self._image)
        else:
            blt_floatbgra(self._film.image, self._image)

    def add(self, name, obj): #add material, shape, light etc...
        if isinstance(obj, Shape):
            self._shp_mgr.add(name, obj)
            #TODO material exist dont assign default think!!!
            #self.assign_material(name, self._default_material)
        #elif isinstance(obj, Material) or isinstance(obj, Light) or isinstance(obj, EnvironmentLight):
        #    self._shader.add(name, obj)
        else:
            raise ValueError("Unknown type of object!") #TODO log not exception !!! exception is just for testing
        self._ready = False


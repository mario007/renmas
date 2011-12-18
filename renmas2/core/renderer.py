
from tdasm import Tdasm, Runtime
from ..samplers import RandomSampler, RegularSampler
from ..cameras import Pinhole
from ..integrators import Raycast, IsectIntegrator
from ..shapes import Shape
from ..lights import Light
from ..macros import MacroSpectrum, MacroCall, arithmetic128, arithmetic32, broadcast,\
                                        macro_if, dot_product, normalization
from .intersector import Intersector
from .film import Film
from .methods import create_tiles
from .shader import Shader
from .material import Material
from .structures import Structures

from .factory import Factory

class Renderer:
    def __init__(self):
        self._ready = False
        self._default_values()
        self._default_objects()

    def _default_objects(self):
        self._intersector = Intersector(self)
        self._integrator = IsectIntegrator(self)
        #self._integrator = Raycast(self)
        #self._sampler = RegularSampler(self._width, self._height)
        self._sampler = RandomSampler(self._width, self._height, spp=self._spp)
        self._spp = self._sampler._spp
        self._film = Film(self._width, self._height, self._spp)
        eye = (10, 10, 10)
        lookat = (0, 0, 0)
        distance = 400
        self._camera = Pinhole(eye, lookat, distance)
        self._shader = Shader()
        self.structures = Structures(self) 
        self.factory = Factory()
        self._assembler = self._create_assembler()
        #create default material TODO

    def _create_assembler(self):
        assembler = Tdasm()
        self._macro_call = macro_call = MacroCall()
        assembler.register_macro('call', macro_call.macro_call)
        assembler.register_macro('eq128', arithmetic128)
        assembler.register_macro('eq32', arithmetic32)
        assembler.register_macro('broadcast', broadcast)
        assembler.register_macro('if', macro_if)
        assembler.register_macro('dot', dot_product)
        assembler.register_macro('normalization', normalization)
        self._macro_spectrum = MacroSpectrum(self)
        assembler.register_macro('spectrum', self._macro_spectrum.macro_spectrum)
        return assembler

    def _default_values(self):
        self._width =  200 
        self._height = 200 
        self._spp = 1 
        self._threads = 1
        self._max_samples = 100000 #max samples in tile
        self._pixel_size = 1.0
        self._spectrum_rendering = False
        self._nspectrum_samples = 8 
        self._start_lambda = 380
        self._end_lambda = 720
        self._default_material = "default" #name of default material

    def set_spec(self, value):
        self._spectrum_rendering = bool(value)
        #TODO prepare evething else needed for spectrum rendering
    def get_spec(self):
        return self._spectrum_rendering
    spectrum_rendering = property(get_spec, set_spec)

    @property
    def nspectrum_samples(self):
        return self._nspectrum_samples

    @property
    def spectrum_region(self):
        return (self._start_lambda, self._end_lambda)

    @property
    def camera(self):
        return self._camera

    @property
    def macro_call(self):
        return self._macro_call

    @property
    def assembler(self):
        return self._assembler

    def spectrum_parameters(self, nsamples, start_lambda, end_lambda):
        n = self._int(self._nspectrum_samples, nsamples)
        n = abs(n)
        if n > 7:
            self._nspectrum_samples = n - (n%8) #round samples 
        self._start_lambda = self._int(self._start_lambda, start_lambda)
        self._end_lambda = self._int(self._end_lambda, end_lambda)

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
        self._tiles2 = list(self._tiles)
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
        elif isinstance(obj, Material) or isinstance(obj, Light):
            self._shader.add(name, obj)
        else:
            raise ValueError("Unknown type of object!") #TODO log not exception !!! exception is just for testing
        self._ready = False

    def assign_material(self, shape, material):
        mat = self._shader.mat_idx(material) 
        if mat is None:
            #TODO Log
            return False
        shape = self._intersector.shape(shape)
        if shape is None:
            # TODO Log
            return False
        shape.material = mat 
        self._intersector.update(shape)
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

    def save_project(self, full_path):
        pass

    def load_project(self, full_path):
        pass

    def export_project(self, full_path):
        pass

    def import_project(self, full_path):
        pass

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


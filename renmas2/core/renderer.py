
import time
import pickle
from tdasm import Tdasm, Runtime
from ..samplers import RandomSampler, RegularSampler
from ..cameras import Pinhole
from ..integrators import Raycast, IsectIntegrator, Pathtracer
from ..shapes import Shape
from ..lights import Light, EnvironmentLight
from ..macros import MacroSpectrum, MacroCall, arithmetic128, arithmetic32, broadcast,\
                                        macro_if, dot_product, normalization, cross_product
from ..materials import HemisphereCos
from ..tone_mapping import PhotoreceptorOperator, ReinhardOperator, ToneMapping
from .intersector import Intersector
from .film import Film
from .methods import create_tiles
from .shader import Shader
from .material import Material
from .structures import Structures
from .spectrum_converter import SpectrumConverter
from .logger import log
from .spd_loader import SPDLoader

from .factory import Factory

# class that hold whole all part of project for serialization
class _Scene:
    def __init__(self):
        self.options = {}

class Renderer:
    def __init__(self):
        self._ready = False
        self._default_values()
        self._default_objects()

    def _default_objects(self):
        self._converter = SpectrumConverter(self)
        self._intersector = Intersector(self)
        #self._integrator = IsectIntegrator(self)
        #self._integrator = Raycast(self)
        self._integrator = Pathtracer(self)
        #self._sampler = RegularSampler(self._width, self._height)
        self._sampler = RandomSampler(self._width, self._height, spp=self._spp)
        self._spp = self._sampler._spp
        self._film = Film(self._width, self._height, self._spp, self)
        self._camera = Pinhole(eye=(0,0,10), lookat=(0,0,0), distance=400)
        self._shader = Shader(self)
        self._structures = Structures(self) 
        self._factory = Factory()
        self._assembler = self._create_assembler()
        #self._tone_mapper = PhotoreceptorOperator()
        self._tone_mapper = ReinhardOperator()
        self._spd_loader = SPDLoader()

        #creation of default material
        mat = Material(self.converter.zero_spectrum())
        s = self.converter.create_spectrum((0.00, 0.77, 0.11))
        lamb = self.factory.create_lambertian(s)
        mat.add(lamb)
        self.shader.add(self._default_material, mat)
        sampling = HemisphereCos()
        mat.add(sampling)

    def get_log(self):
        return log.handlers[0].get_log()

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
        assembler.register_macro('cross', cross_product)
        self._macro_spectrum = MacroSpectrum(self)
        assembler.register_macro('spectrum', self._macro_spectrum.macro_spectrum)
        return assembler

    def _default_values(self):
        self._width =  600 
        self._height = 600 
        self._spp = 1 
        self._threads = 1 
        self._max_samples = 100000 #max samples in tile
        self._pixel_size = 1.0
        self._spectrum_rendering = False 
        self._nspectrum_samples = 32 
        self._start_lambda = 380
        self._end_lambda = 720
        self._default_material = "default" #name of default material
        self._asm = False 
        self._tone_mapping = True 
        self._current_pass = 0

    def _set_spec(self, value):
        self._spectrum_rendering = bool(value)
        self._ready = False 
        self.shader.convert_spectrums()
        #TODO -- resampled spectrums 
        #TODO prepare evething else needed for spectrum rendering
    def _get_spec(self):
        return self._spectrum_rendering
    spectral_rendering = property(_get_spec, _set_spec)

    def _set_tone_mapping(self, value):
        try:
            self._tone_mapping = bool(value) 
        except:
            pass
        self.tone_map()
    def _get_tone_mapping(self):
        return self._tone_mapping
    tone_mapping = property(_get_tone_mapping, _set_tone_mapping)

    def _set_tone_mapping_operator(self, value):
        if isinstance(value, ToneMapping):
            self._tone_mapper = value 
        self.tone_map()
    def _get_tone_mapping_operator(self):
        return self._tone_mapper
    tone_mapping_operator = property(_get_tone_mapping_operator, _set_tone_mapping_operator)

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

    @property
    def intersector(self):
        return self._intersector

    @property
    def structures(self):
        return self._structures

    @property
    def factory(self):
        return self._factory

    @property
    def sampler(self):
        return self._sampler

    @property
    def film(self):
        return self._film

    @property
    def converter(self):
        return self._converter

    @property
    def shader(self):
        return self._shader

    @property
    def spd(self):
        return self._spd_loader

    def spectrum_parameters(self, nsamples, start_lambda, end_lambda):
        n = self._int(self._nspectrum_samples, nsamples)
        n = abs(n)
        if n > 7:
            self._nspectrum_samples = n - (n%8) #round samples 
        self._start_lambda = self._int(self._start_lambda, start_lambda)
        self._end_lambda = self._int(self._end_lambda, end_lambda)
        ##TODO -- resampling spectrums 

    def _set_asm(self, value):
        self._asm = bool(value)
        if self._asm: self._max_samples = 200000 
        else: self._max_samples = 10000
        self._ready = False
    def _get_asm(self):
        return self._asm
    asm = property(_get_asm, _set_asm)

    def resolution(self, width, height):
        width = self._int(self._width, width)
        height = self._int(self._height, height)
        self._width = width
        self._height = height
        self._film.set_resolution(width, height)
        self._sampler.set_resolution(width, height)
        self._tiles3 = create_tiles(self._width, self._height, 1, self._max_samples, self._threads)

    def _set_spp(self, value):
        n = self._int(self._spp, value)
        self._sampler.spp(n)
        self._spp = self._sampler._spp 
        self._film.set_nsamples(self._spp)
    def _get_spp(self):
        return self._spp
    spp = property(_get_spp, _set_spp)

    def _set_pixel_size(self, value):
        size = self._float(self._pixel_size, value)
        self._pixel_size = size
        self._sampler.set_pixel_size(self._pixel_size)
    def _get_pixel_size(self):
        return self._pixel_size
    pixel_size = property(_get_pixel_size, _set_pixel_size)

    def tone_map(self): #tone mapping of whole image
        if self._tone_mapping: 
            f = self._film
            self._tone_mapper.tone_map(f.frame_buffer, f.image, 0, 0, f.image.width, f.image.height) 
        else:
            self._film.blt_image_to_buffer()

    def set_samplers(self, samplers): #Tip: First solve for one sampler
        self._sampler = samplers[0]
        self._samplers = samplers
        self._ready = False

    def _set_threads(self, value):
        n = self._int(self._threads, value)
        nc = abs(n)
        if nc > 32: nc = 32 #max number of threads
        self._threads = nc
        self._ready = False
    def _get_threads(self):
        return self._threads
    threads = property(_get_threads, _set_threads)

    def prepare(self): #prepare everything that is needed for rendering 
        start = time.clock()
        self._tiles = create_tiles(self._width, self._height, self._spp, self._max_samples, self._threads)
        self._tiles2 = list(self._tiles)
        self._tiles3 = create_tiles(self._width, self._height, 1, self._max_samples, self._threads)
        self._intersector.prepare()
        self._integrator.prepare()
        self._film.reset()
        self._ready = True
        self._current_pass = 0
        end = time.clock()
        log.info("Time that took to prepare renderer for rendering: " + str(end-start) + " seconds.")

    def reset(self): #restart of rendering
        self._current_pass = 0

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
            #TODO material exist dont assign default think!!!
            self.assign_material(name, self._default_material)
        elif isinstance(obj, Material) or isinstance(obj, Light) or isinstance(obj, EnvironmentLight):
            self._shader.add(name, obj)
        else:
            raise ValueError("Unknown type of object!") #TODO log not exception !!! exception is just for testing
        self._ready = False

    def assign_material(self, shape_name, mat_name):
        mat_idx = self._shader.mat_idx(mat_name) 
        if mat_idx is None:
            log.info("Material " + mat_name + " doesn't exist!!!")
        shape = self._intersector.shape(shape_name)
        if shape is None:
            log.info("Shape " + shape_name + " doesn't exist!!!")
        if mat_idx is None or shape is None:
            return False
        shape.material = mat_idx 
        self._intersector.update(shape)
        self._ready = False #TODO -- think -- ready = False is not needed here
        return True
        
    def render_old(self):
        if not self._ready: self.prepare()
        if not self._ready: return None #unexpected error ocur!!!! TODO
        try:
            tile = self._tiles.pop()
        except IndexError:
            return False # All tiles are rendererd
        
        self._integrator.render(tile)
        return True

    def render(self):
        if not self._ready: self.prepare()
        if not self._ready: return None #unexpected error ocur!!!! TODO
        self._film.set_pass(self._current_pass) #required for assembly rendering
        for tile in self._tiles3:
            self._integrator.render(tile)

        self._current_pass += 1
        if self._current_pass >= self._spp:
            return False
        else:
            return True

    def save_project(self, path):
        sc = _Scene()
        options = {"width": self._width, "height": self._height, "spp": self._spp, "threads": self._threads, 
                "pixel_size": self._pixel_size,
                "spectral_rendering": self._spectrum_rendering, "nsamples": self._nspectrum_samples,
                "start_lambda": self._start_lambda, "end_lambda": self._end_lambda,
                "asm": self._asm, "tone": self._tone_mapping}
        sc.options = options

        try:
            f = open(path, "wb")
            pickle.dump(sc, f)
            log.info("Project sucssesfuly saved.")
        except:
            log.info("Saving project failed, make sure that path is valid!")

    def load_project(self, path):
        try:
            f = open(path, "rb")
            sc = pickle.load(f)
            log.info("Project sucessfuly load.")
        except:
            log.info("Project loading failed, make sure that path is valid!")
            return
        
        options = sc.options
        self.spectral_rendering = options['spectral_rendering'] 
        self.spectrum_parameters(options['nsamples'], options['start_lambda'], options['end_lambda'])
        self.resolution(options['width'], options['height'])
        self.spp = options['spp']
        self.threads = options['threads'] 
        self.pixel_size = options['pixel_size'] 
        self.asm = options['asm']
        self.tone_mapping = options['tone']

        self._ready = False
        self._current_pass = 0

    def export_project(self, path):
        pass

    def import_project(self, path):
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


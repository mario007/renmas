
import time
from tdasm import Runtime
from sdl import ImagePRGBA, ImageRGBA, Vector3, SampledManager
from hdr import Tmo

from .camera import Camera
from .samplers import RegularSampler
from .shp_mgr import ShapeManager
from .linear import LinearIsect
from .integrator import Integrator
from .light import LightManager
from .material import MaterialManager
from .shadepoint import register_sampled_shadepoint, register_rgb_shadepoint
from .spec_shaders import sampled_to_vec_shader, rgb_to_vec_shader

from .parse_scene import import_scene


class Renderer:
    def __init__(self):
        self._spectral = False
        self._sam_mgr = SampledManager()
        if self._spectral:
            register_sampled_shadepoint(self._sam_mgr)
        else:
            register_rgb_shadepoint()

        self.sampler = RegularSampler(width=512, height=512,
                                      pixelsize=1.0, nthreads=1)
        self.camera = Camera(eye=Vector3(5.0, 5.0, 5.0),
                             lookat=Vector3(0.0, 0.0, 0.0), distance=200)
        self.camera.load('pinhole')
        self.shapes = ShapeManager()
        self.intersector = LinearIsect(self.shapes)
        self.materials = MaterialManager()
        self.lights = LightManager()
        self.filter = None
        self.integrator = Integrator()
        #self.integrator.load('isect')
        self.integrator.load('test')

        self.tone_mapping = Tmo()
        self.tone_mapping.load('exp')

        self._ready = False
        self._create_hdr_buffer()

    @property
    def spectral(self):
        return self._spectral

    @property
    def sam_mgr(self):
        return self._sam_mgr

    def _create_hdr_buffer(self):
        width, height = self.sampler.get_resolution()
        self._hdr_buffer = ImagePRGBA(width, height)
        self._hdr_buffer.clear()
        self._hdr_output = ImagePRGBA(width, height)

    def prepare(self):
        self._create_hdr_buffer()
        runtimes = [Runtime() for i in range(self.sampler.nthreads)]

        self.sampler.create_shader()
        self.sampler.compile()
        self.sampler.prepare(runtimes)
        self.sampler.reset()

        self.camera.compile()
        self.camera.prepare(runtimes)

        self.intersector.prepare_accel()
        self.intersector.compile()
        self.intersector.prepare(runtimes)

        self.lights.compile_shaders(self.sam_mgr, self.spectral)
        self.lights.prepare_shaders(runtimes)

        self.materials.compile_shaders(self.sam_mgr, self.spectral)
        self.materials.prepare_shaders(runtimes)

        if self.spectral:
            spec_to_vec = sampled_to_vec_shader(self.sam_mgr)
        else:
            spec_to_vec = rgb_to_vec_shader()
        spec_to_vec.compile()
        spec_to_vec.prepare(runtimes)

        shaders = [self.sampler.shader, self.camera.shader,
                   self.intersector.shader, self.lights.rad_shader,
                   self.lights.nlights_shader, self.materials.ref_shader,
                   spec_to_vec, self.intersector.visible_shader]

        self.integrator.compile(shaders)
        self.integrator.prepare(runtimes)

        self._ready = True

    def reset(self):
        self._create_hdr_buffer()
        self.sampler.reset()

    def render(self):
        """Execute rendering of one sample for each pixel. If we have
        multiple samples per pixel we must call this function multiple
        times. Function return True if all samples are processed otherwise
        False.
        """

        if not self._ready:
            self.prepare()

        if not self.sampler.has_more_samples():
            return True

        start = time.clock()
        self.integrator.execute(self._hdr_buffer)
        end = time.clock()
        print(end-start)
        # print (self.integrator.shader._asm_code)
        # self.integrator.shader._mc.print_machine_code()
        self.sampler.increment_pass()

        return False

    def tmo(self):
        if self._hdr_buffer is not None:
            self.tone_mapping.tmo(self._hdr_buffer, self._hdr_output)

    def save(self, filename):
        pass

    def load(self, filename):

        import_scene(filename, self)
        self._ready = False

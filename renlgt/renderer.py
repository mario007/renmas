
import time
import os
import os.path

from tdasm import Runtime
from sdl import ImagePRGBA, ImageRGBA, Vector3, RGBManager, SampledManager
from hdr import Tmo

from .camera import Camera
from .samplers import RegularSampler
from .shp_mgr import ShapeManager
from .linear import LinearIsect
from .integrator import Integrator
from .light import LightManager, AreaLight
from .material import MaterialManager
from .shadepoint import register_prototypes
from .spec_shaders import spectrum_to_rgb_shader, luminance_shader
from .flt import SampleFilter
from .shader_lib import shaders_functions

from .parse_scene import import_scene


class Renderer:
    def __init__(self, color_mgr=RGBManager()):
    # def __init__(self, color_mgr=SampledManager()):
        self._color_mgr = color_mgr
        register_prototypes(color_mgr.zero())

        self.sampler = RegularSampler(width=512, height=512,
                                      pixelsize=1.0, nthreads=1)
        self.camera = Camera(eye=Vector3(5.0, 5.0, 5.0),
                             lookat=Vector3(0.0, 0.0, 0.0), distance=200)
        self.camera.load('pinhole')
        self.shapes = ShapeManager()
        self.intersector = LinearIsect(self.shapes)
        self.materials = MaterialManager()
        self.lights = LightManager()
        self.filter = SampleFilter()
        self.filter.load('box')
        self.integrator = Integrator()
        # self.integrator.load('isect')
        self.integrator.load('test', self._color_mgr)

        self.tone_mapping = Tmo()
        self.tone_mapping.load('exp')

        self._ready = False
        self._create_hdr_buffer()

    @property
    def color_mgr(self):
        return self._color_mgr

    def _create_defaults(self):
        pass

    def _create_hdr_buffer(self):
        width, height = self.sampler.get_resolution()
        self._hdr_buffer = ImagePRGBA(width, height)
        self._hdr_buffer.clear()
        self._hdr_output = ImagePRGBA(width, height)

    def prepare(self):
        self._create_hdr_buffer()
        self.sync_area_lights()
        runtimes = [Runtime(code=4) for i in range(self.sampler.nthreads)]

        shaders_funcs = shaders_functions()
        for s in shaders_funcs:
            s.compile()
            s.prepare(runtimes)

        self.sampler.create_shader()
        self.sampler.compile()
        self.sampler.prepare(runtimes)
        self.sampler.reset()

        self.camera.compile()
        self.camera.prepare(runtimes)

        self.filter.compile()
        self.filter.prepare(runtimes)

        self.intersector.prepare_accel()
        self.intersector.compile()
        self.intersector.prepare(runtimes)

        self.lights.compile_shaders(self._color_mgr)
        self.lights.prepare_shaders(runtimes)
        for shape in self.lights.shapes_to_update():
            self.shapes.update(shape)

        lum_shader = luminance_shader(self._color_mgr)
        lum_shader.compile(color_mgr=self._color_mgr)
        lum_shader.prepare(runtimes)
        spec_to_rgb_shader = spectrum_to_rgb_shader(self._color_mgr)
        spec_to_rgb_shader.compile(color_mgr=self._color_mgr)
        spec_to_rgb_shader.prepare(runtimes)

        self.materials.compile_shaders(self._color_mgr, shaders_funcs + [lum_shader])
        self.materials.prepare_shaders(runtimes)

        shaders = [self.sampler.shader, self.camera.shader,
                   self.intersector.shader, self.lights.rad_shader,
                   self.lights.nlights_shader, self.lights.env_shader,
                   self.lights.emission_shader, self.materials.ref_shader,
                   spec_to_rgb_shader, self.intersector.visible_shader,
                   lum_shader, self.materials.sampling_shader,
                   self.materials.pdf_shader, self.filter.shader]

        self.integrator.compile(shaders)
        self.integrator.prepare(runtimes)

        self._ready = True

    def reset(self):
        if self._hdr_buffer is not None:
            self._hdr_buffer.clear()
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

        self.integrator.execute(self._hdr_buffer)
        # print (self.integrator.shader._asm_code)
        # self.integrator.shader._mc.print_machine_code()
        self.sampler.increment_pass()

        if not self.sampler.has_more_samples():
            return True

        return False

    def tmo(self):
        if self._hdr_buffer is not None:
            self.tone_mapping.tmo(self._hdr_buffer, self._hdr_output)

    def save(self, filename):
        f = open(filename, mode='w')
        directory = os.path.dirname(os.path.abspath(f.name))
        mesh_dir = os.path.join(directory, 'meshes')
        if not os.path.isdir(mesh_dir):
            os.mkdir(mesh_dir)

        txt = self.sampler.output()
        f.write(txt)
        f.write('\n')
        txt = self.camera.output()
        f.write(txt)
        f.write('\n')
        txt = self.lights.output()
        f.write(txt)
        f.write('\n')
        txt = self.materials.output()
        f.write(txt)
        f.write('\n')

        for shape in self.shapes:
            text = 'Shape\n'
            fname = self.shapes.name(shape) + '.data'
            relative_name = os.path.join('meshes', fname)
            text += shape.output(directory, relative_name)
            text += 'name = %s\n' % self.shapes.name(shape)
            text += 'material = %s\n' % self.materials.name(shape.mat_idx)
            text += 'End\n\n'
            f.write(text)

        f.close()

    def load(self, filename):

        import_scene(filename, self)
        self._ready = False

    def sync_area_lights(self):
        for shape in self.shapes:
            material = self.materials.material(index=shape.mat_idx)
            area_light = self.lights.arealight(shape)
            if material.is_emissive() and area_light is None:
                light = AreaLight(shape=shape, material=material)
                light.load('general', self._color_mgr)
                name = 'arealight_%i' % id(light)
                self.lights.add(name, light)
            elif not material.is_emissive() and area_light is not None:
                area_light.shape.light_id = -1
                self.lights.remove(light=area_light)
                self.shapes.update(area_light.shape)


import pickle
import os.path
from tdasm import Runtime
from .parse_scene import parse_scene
from ..base import arg_list, arg_map, Vec3, Vec4, ColorManager, Spectrum
from ..base import BaseShader, BasicShader, ImageRGBA, ImagePRGBA, ImageBGRA 
from ..samplers import Sample
from ..shapes import ShapeManager, LinearIsect
from ..utils import blt_prgba_to_bgra
from ..integrators import get_integrator_code

from .light import LightManager
from .mat import MaterialManager
from ..tone import ReinhardOperator

class Project:
    """This class is responsible holding all data object that will
    be saved in project file. Thease objects are Sampler, Camera,
    Shapes, Materials, Lights.
    """
    def __init__(self):
        self.sampler = None
        self.camera = None
        self.integrators_code = None
        self.nthreads = 1
        self.shapes = ShapeManager()
        self.col_mgr = ColorManager(spectral=False)
        self.lgt_mgr = LightManager()
        self.mat_mgr = MaterialManager()

    @staticmethod
    def load(fname):
        """This static method is used for parsing text file who is hodling
        description of whole scene. Some of stuff that that are in file is
        description of lights, materials, shapes etc..."""

        if not os.path.exists(fname):
            raise ValueError("File %s doesn't exist!" % fname)
        project = Project()
        fobj = open(fname)
        parse_scene(fobj, project)

        return project

    def dump(self, fname):
        """
        Dumps description of whole scene in ascii text file.
        """
        pass

    def set_material(self, shape_name, material_name):
        shape = self.shapes.shape(shape_name)
        if shape is None:
            return #TODO Do something
        idx = self.mat_mgr.index(material_name)
        if idx is None:
            return #TODO Do something
        shape.material_idx = idx
        self.shapes.update(shape)

class Film(BaseShader):
    """Shader that used store samples in image."""

    def __init__(self):
        code = self._shader_code()
        super(Film, self).__init__(code)
        self._hdr_image = ImagePRGBA(10, 10)
        self._ldr_image = ImagePRGBA(10, 10)
        self._output_img = ImageBGRA(10, 10)

    def _shader_code(self):
        code = """

x = sample.ix
y = sample.iy
rgba = get_rgba(hdr_image, x, y)

acum_weight = rgba[3]
rgba = rgba * acum_weight

flt_weight = 0.99 # box filter
rgb = rgb * flt_weight

new_col = float4(rgb[0], rgb[1], rgb[2], 1.0)
new_col = new_col + rgba

acum_weight = acum_weight + flt_weight

new_col = new_col * (1.0 / acum_weight)
new_col[3] = acum_weight

set_rgba(hdr_image, x, y, new_col)

        """
        return code

    def set_resolution(self, width, height):
        """Set resolution of image buffers."""
        self._hdr_image = ImagePRGBA(width, height)
        self._ldr_image = ImagePRGBA(width, height)
        self._output_img = ImageBGRA(width, height)
        self.clear()

    def get_props(self, nthreads):
        props = {'hdr_image': self._hdr_image}
        return props

    def arg_map(self):
        args = arg_map([('hdr_image', ImagePRGBA)])
        return args

    def arg_list(self):
        return arg_list([('sample', Sample), ('rgb', Vec3)])

    def method_name(self):
        return 'add_sample'

    def standalone(self):
        return False

    def clear(self):
        """Populate buffers with zeroes."""
        self._hdr_image.clear()
        self._ldr_image.clear()
        self._output_img.clear()

class Renderer:
    """Main class that is used for holding all the parts together that
    are required for rendering of image."""
    def __init__(self):
        self._project = Project()
        self._integrator = None
        self._ready = False
        self._runtimes = None
        self._pass = 0
        self._film = Film()
        self._intersector = None

    def set_resolution(self, width, height):
        """Set resolution of output image. """
        self._ready = False


    def save_project(self, fname):
        """Save project."""
        fobj = open(fname, 'wb')
        pickle.dump(self._project, fobj)

    def open_project(self, fname):
        """Open existing project file."""
        fobj = open(fname, 'rb')
        self._project = pickle.load(fobj)
        self._ready = False

    def parse_scene_file(self, fname):
        """Parse description scene file."""
        self._project = Project.load(fname)
        self._ready = False

    def prepare_lights(self, runtimes):
        return self._project.lgt_mgr.prepare_illuminate('light_radiance', runtimes)

    def prepare_materials(self, runtimes):
        return self._project.mat_mgr.prepare_bsdf('bsdf', runtimes)

    def prepare_materials_samples(self, runtimes):
        return self._project.mat_mgr.prepare_sample('sample_bsdf', runtimes)

    def prepare_materials_pdf(self, runtimes):
        return self._project.mat_mgr.prepare_pdf('pdf_bsdf', runtimes)

    def prepare(self):
        """Prepare renderer for rendering. Compile all shaders. Build
        acceleration structures."""
        if self._project is None:
            raise ValueError("Project is not created!")
        nthreads = self._project.nthreads
        self._runtimes = [Runtime() for n in range(nthreads)]

        if self._project.sampler is None:
            raise ValueError("Sampler is not defined!")
        self._project.sampler.prepare(self._runtimes)
        if self._project.camera is None:
            raise ValueError("Camera is not defined!")
        self._project.camera.prepare(self._runtimes)

        self._film.prepare(self._runtimes)

        width = self._project.sampler.width
        height = self._project.sampler.height
        self._film.set_resolution(width, height)
        self._film.update()

        self._prepare_integrator(self._runtimes)
        self._pass = 0
        self._ready = True

    def set_integrator_code(self, code):
        """Set code for shader that is responsible for rendering."""
        self._project.integrators_code = code

    def _prepare_integrator(self, runtimes):
        """Compile shader who is holding rendering algorithm."""

        #code = get_integrator_code('raycast')
        code = get_integrator_code('pathtracer')
        self._project.integrators_code = code
        if self._project.integrators_code is None:
            code = get_integrator_code('simple2D')
            self._project.integrators_code = code
        code = self._project.integrators_code

        self._integrator = BasicShader(code, {}, col_mgr=self._project.col_mgr)
        sam_sh = self._project.sampler.shader
        cam_sh = self._project.camera.shader
        film_sh = self._film.shader

        isect_sh = self._isect_shader(runtimes)
        visible_sh = self._visible_shader(runtimes)

        lgt_sh = self.prepare_lights(runtimes)
        mat_sh = self.prepare_materials(runtimes)
        sam_mat_sh = self.prepare_materials_samples(runtimes)
        pdf_sh = self.prepare_materials_pdf(runtimes)

        nlight_sh = self._project.lgt_mgr.nlights_shader('number_of_lights', runtimes)

        self._integrator.prepare(runtimes, [sam_sh, cam_sh, film_sh, isect_sh,
            lgt_sh, mat_sh, nlight_sh, visible_sh, sam_mat_sh, pdf_sh])

    def _isect_shader(self, runtimes):
        if self._intersector is None:
            self._intersector = LinearIsect(self._project.shapes)

        shader = self._intersector.isect_shader(runtimes)
        shader.prepare(runtimes)
        return shader

    def _visible_shader(self, runtimes):
        if self._intersector is None:
            self._intersector = LinearIsect(self._project.shapes)

        shader = self._intersector.visible_shader(runtimes)
        shader.prepare(runtimes)
        return shader

    def render(self):
        """Execute rendering of one sample for each pixel. If we have
        multiple samples per pixel we must call this function multiple
        times. Function return True if all samples are processed otherwise
        False."""

        if not self._ready:
            self.prepare()

        if not self._project.sampler.has_more_samples(self._pass):
            return True 
        
        self._project.sampler.set_pass(self._pass)
        self._integrator.execute()
        self._pass += 1

        #TODO -- tone mapping

        return not self._project.sampler.has_more_samples(self._pass)

    def output_image(self):
        img = self._film._hdr_image
        img2 = self._film._output_img
        reinhard = ReinhardOperator()
        reinhard.tone_map(img, img2)
        #blt_prgba_to_bgra(img, img2)
        return self._film._output_img


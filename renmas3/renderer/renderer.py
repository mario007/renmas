
import pickle
import os.path
from tdasm import Runtime
from .parse_scene import parse_scene
from ..base import arg_list, arg_map, Vec3
from ..base import BaseShader, BasicShader, ImageRGBA, ImagePRGBA, ImageBGRA 
from ..samplers import Sample
from ..shapes import ShapeManager, LinearIsect


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
#add_sample(sample, spectrum)
set_rgb(hdr_image, sample.ix, sample.iy, spectrum)

        """
        return code

    def set_resolution(self, width, height):
        """Set resolution of image buffers."""
        self._hdr_image = ImagePRGBA(width, height)
        self._ldr_image = ImagePRGBA(width, height)
        self._output_img = ImageBGRA(width, height)

    def get_props(self, nthreads):
        props = {'hdr_image': self._hdr_image}
        return props

    def arg_map(self):
        args = arg_map([('hdr_image', ImagePRGBA)])
        return args

    def arg_list(self):
        return arg_list([('sample', Sample), ('spectrum', Vec3)])

    def method_name(self):
        return 'add_sample'

    def standalone(self):
        return False

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
        pass


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

        if self._project.integrators_code is None:
            raise ValueError("Integrator code is missing!")
        code = self._project.integrators_code
        self._integrator = BasicShader(code, {})
        sam_sh = self._project.sampler.shader
        cam_sh = self._project.camera.shader
        film_sh = self._film.shader

        isect_sh = self._isect_shader(runtimes)
        self._integrator.prepare(runtimes, [sam_sh, cam_sh, film_sh, isect_sh])

    def _isect_shader(self, runtimes):
        if self._intersector is None:
            self._intersector = LinearIsect(self._project.shapes)

        shader = self._intersector.isect_shader(runtimes)
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


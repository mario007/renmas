
import renmas
from ..camera import PinholeCamera 
from ..samplers import RandomSampler
from ..maths import Vector3
from . import Film
from .logger import log
from tdasm import Runtime
import time

## Main interface to renderer. 
# All calls to renderer must go through this interface
class Renderer:
    def __init__(self):
        # some default objects 
        self._film = Film(200, 200, 1)
        self._sampler = RandomSampler(200, 200, 1, 1.0)
        eye = Vector3(10.0, 10.0, 10.0)
        eye = Vector3(-100.0, 10.0, -60.0)
        lookat = Vector3(0.0, 0.0, 0.0)
        lookat = Vector3(-220.0, 80.0, 14.0)
        self._camera = PinholeCamera(eye, lookat, 400.0)

        # containers for lights  
        self._light_c = {}
        self._light_l = [] # because shading routine need list of lights to be fast

        # containers for materials
        self._material_c = {} 
        self._materials_l = []
        self._materials_idx = {}

        # containers for shapes 
        self._shape_names = {} #name:shape
        self._shape_addr = {} # shape:idx  - using index in dynamic array we can calculate address
        self._shape_arrays = {} # DynamicArrays for assembly rendering

        self._ready = False #True means that everything is ready for rendering
        self._world_grid = True # True means that we MUST build world grid
        self._grid = None # world grid
        self._world_arrays = {} # Dynamic array for world grid

        # default options
        self.set_rendering_algorithm("pathtracer_asm")
        self._tiles = []

        # default material for shapes that doesnt have valid material specified
        mat = renmas.materials.Material()
        sam = renmas.materials.HemisphereCos()
        spectrum = renmas.core.Spectrum(0.66, 0.77, 0.88)
        lamb = renmas.materials.LambertianBRDF(spectrum)
        mat.add_component(lamb)
        mat.add_sampling(sam)
        self.add_material("default_material", mat)

    def reset(self):
        pass

    def prepare(self):
        log.info("Warming up for rendering!")
        #Warm-up phase for rendering
        #Check evereything and build acceleration structures, and acceleration for mesh if needed
        if len(self._light_l) == 0:
            log.info("There are no lights in the scene!!!")
            return False

        nshapes = len(self._shape_names) 

        #MESH???? - acceleration structures

        if nshapes == 0:
            log.info("There are no shapes in the scene!!!")
            return False

        if self._world_grid:
            self._grid = grid = renmas.shapes.Grid()
            lst_shapes = list(self._shape_names.values())
            grid.setup(lst_shapes, self)
            self._world_grid = False

        self._tiles = self._generate_tiles()

        self._build_runtime()

        self._ready = True
        return True

    def _build_runtime(self):
        start = time.clock()
        self._runtime = runtime = Runtime()
        self._sampler.get_sample_asm(runtime, "get_sample")
        self._camera.ray_asm(runtime, "generate_ray")

        self._world_arrays = {} 
        darr = renmas.utils.DynamicArray(self._grid.struct())
        darr.add_instance(self._grid.attributes())
        self._world_arrays[type(self._grid)] = darr

        renmas.shapes.linear_isect_asm(runtime, "scene_isect", self._world_arrays)
        renmas.shapes.visible_asm(runtime, "visible", "scene_isect")

        renmas.core.generate_shade(runtime, "shade", "visible", self)
        self._film.add_sample_asm(runtime, "add_sample")

        if self._algorithm_name == "raycast_asm":
            renmas.integrators.prepare_raycast_asm(runtime) #alogorithm
        else:
            renmas.integrators.prepare_pathtracer_asm(runtime) #alogorithm
        end = time.clock()

        log.info("Time to builde Runtime object: " + str(end-start))

        return runtime

    def set_camera(self, camera):
        self._camera = camera
        self._ready = False #we need new assembly code

    def get_camera(self):
        # think!!! camera must take care when data_section when something changes
        # camera must accept array of runtime objects not just one!!!! same holds for other objects
        self._ready = False
        return self._camera
    
    def set_resolution(self, width, height):
        self._film.set_resolution(int(width), int(height))
        self._sampler.resolution(int(width), int(height))
        self._ready = False

    def get_resolution(self):
        return self._film.get_resolution()

    def set_pixel_size(self, size):
        self._sampler.pixel_size(float(size))

    def get_pixel_size(self):
        return self._sampler.get_pixel_size()

    def set_sampler(self, sampler):
        self._sampler = sampler #see camera instructions, same holds here
        self._ready = False

    def get_sampler(self):
        return self._sampler

    def get_samples_per_pixel(self):
        return self._sampler.nsamples()

    def set_samples_per_pixel(self, num):
        self._sampler.set_samples_per_pixel(num)
        ns = self.get_samples_per_pixel()
        self._film.set_nsamples(ns)

    def add_material(self, name, material):
        if name in self._material_c:
            log.info("Material with that name allready exist!!!")
            return
        self._material_c[name] = (material, len(self._materials_l))
        self._materials_idx[len(self._materials_l)] = material
        self._materials_l.append(material)
        self._ready = False

    def add_brdf(self, name, brdf):
        material = self.material(name)
        if material is None: 
            log.info("Material with that name doesn't exist!!!")
            return 
        material.add_component(brdf)
        self._ready = False

    def add_shape(self, name, shape):
        if name in self._shape_names:
            log.info("Shape with that name allready exist!!!")
            return
        #TODO Check if shape has valid material - put default it it doesn't have
        self._shape_names[name] = shape #name:shape
        # Be very carefull - dynamic are do automatic resize by himself
        if type(shape) not in self._shape_arrays:
            darr = renmas.utils.DynamicArray(shape.struct())
            darr.add_instance(shape.attributes())
            self._shape_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self._shape_arrays[type(shape)]
            idx = darr.num_objects()
            darr.add_instance(shape.attributes())

        self._shape_addr[shape] = idx 
        self._ready = False
        self._world_grid = True 


    def add_light(self, name, light):
        if name in self._light_c:
            log.info("Light with that name allready exist!!!")
            return
        self._light_l.append(light)
        self._light_c[name] = light
        self._ready = False

    def render(self):
        if not self._ready:
            self.prepare()
        if not self._ready:
            return False
        # render using selected algorithm 
        try:
            tile = self._tiles.pop()
        except:
            return True # All tiles are rendererd

        self._algorithm(tile, self)
        return False


    def set_material_to_shape(self, material_name, shape_name):
        mat = self_material(material_name)
        if mat is None:
            log.info("Add material to shape! Material doesn't exist!")
            return False
        shape = self.shape(shape_name)
        if shape is None:
            log.info("Add material to shape! Shape doesn't exist!")
            return False
        #shape must add interface to add material?? TODO
        shape.material = self.material_index(material_name)
        #update of shape in memory
        self._update_shape(shape)

    def _update_shape(self, shape):
        try:
            idx = self._shape_addr[shape]
            darr = self._shape_arrays[type(shape)]
            darr.edit_instance(idx, shape.attributes())
        except:
            log.info("Cannot update shape because shape doesn't exist!")

    def set_rendering_algorithm(self, algorithm):

        if algorithm == "raycast_py":
            self._algorithm = renmas.integrators.raycast_integrator 
            self._algorithm_name = "raycast_py"
        elif algorithm == "pathtracer_py":
            self._algorithm = renmas.integrators.path_integrator
            self._algorithm_name = "pathtracer_py"
        elif algorithm == "raycast_asm":
            self._algorithm = renmas.integrators.raycast_integrator_asm
            self._algorithm_name = "raycast_asm"
        elif algorithm == "pathtracer_asm":
            self._algorithm = renmas.integrators.path_integrator_asm
            self._algorithm_name = "pathtracer_asm"
        else:
            log.info("Specified algorithm " + algorithm + " doesn't exist!!!")
            self._algorithm = renmas.integrators.path_integrator_asm
            self._algorithm_name = "pathtracer_asm"

        self._ready = False

    def get_picture(self, typeOf):
        return self._film.image
        return self._film.frame_buffer

    def shape(self, name):
        if name in self._shape_names:
            return self._shape_names[name]
        else:
            return None

    def material(self, name):
        if name in self._material_c:
            return self._material_c[name][0]
        else:
            return None

    def material_index(self, name):
        if name in self._material_c:
            return self._material_c[name][1]
        else:
            return None 
        
    def _generate_tiles(self):

        width, height = self.get_resolution()

        w = h = 50
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
                tiles.append((i, j, tw, th))
        
        return tiles

    def shape_address(self, shape):
        idx = self._shape_addr.get(shape, None)
        if idx is None: return None

        darr = self._shape_arrays[type(shape)]
        addr = darr.get_addr() + idx * darr.obj_size() 
        return addr

    def _isect(self, ray, min_dist = 999999.0):
        return self._grid.isect(ray, min_dist)


    def _list_lights(self):
        return self._light_l

    def _list_materials(self):
        return self._materials_l

    def _shade(self, hp):

        # direct illumination
        #loop through lights
        lights = self._light_l 
        material = self._materials_idx[hp.material]

        # emisive material
        hp.le = material.le(hp)
        tmp_spec = renmas.core.Spectrum(0.0, 0.0, 0.0) 
        for light in lights:
            if light.L(hp, self) is True: #light is visible
                material.brdf(hp)
                tmp_spec = tmp_spec + (hp.spectrum.mix_spectrum(hp.brdf) * hp.ndotwi)
        hp.spectrum = tmp_spec

        # indirect illumination
        #to calculate next direction
        # first calculate next direction i pdf - next direction is in wi
        material.next_direction(hp)
        return hp

    def _visible(self, p1, p2):

        epsilon = 0.00001
        direction = p2 - p1

        distance = direction.length() - epsilon # self intersection!!! visiblity

        ray = renmas.core.Ray(p1, direction.normalize())
        hp = self._isect(ray, 999999.0)

        if hp is None or hp is False:
            return True
        else:
            if hp.t < distance:
                return False
            else:
                return True


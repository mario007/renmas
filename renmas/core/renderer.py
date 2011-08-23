
from ..camera import PinholeCamera 
from ..samplers import RandomSampler
from ..maths import Vector3
from . import Film
from . import ShapeDatabase
from . import MaterialDatabase
from . import LightDatabase

## Main interface to renderer. 
# All calls to renderer must go through this interface
class Renderer:
    ## Constructor.
    # Create default objects for camera, sampler.
    # Default camera properties (type=perspective, lookat=0,0,0 eye=10,10,10,
    # distance=400).
    # Default sampler is random sampler with 1 samples per pixel.
    # Default resolution of picture is 200x200.
    # Default pixel size is 1.0.
    # @param self The object pointer
    def __init__(self):
        # some default objects 
        self._film = Film(200, 200, 1)
        self._sampler = RandomSampler(200, 200, 1, 1.0)
        eye = Vector3(10.0, 10.0, 10.0)
        lookat = Vector3(0.0, 0.0, 0.0)
        self._camera = PinholeCamera(eye, lookat, 400.0)

        # containers for lights  
        self._light_c = {}
        self._light_l = [] # because shading routine need list of lights

        # containers for materials
        self._material_c = {} 
        self._materials_l = []
        self._materials_idx = {}

        # containers for shapes 
        self._shape_names = {} #name:shape
        self._shape_addr = {} # shape:idx  - using index in dynamic array we can calculate address
        self._shape_arrays = {} # DynamicArrays for assembly rendering

        # very important - if ready is true that means everything is ready for rendering
        self._ready = False
        # world grind must be build before rendering starts
        # if something changes than we need again to build this grid
        self._world_grid = True

    ## Reset
    # Erase all shapes, materials, etc... from renderer and bring renderer to
    # start state, same as when you create new Renderer
    # @param self The object pointer
    def reset(self):
        pass

    ## Prepare renderer for rendering
    # Create all nessesery acceleration structures
    # Create runtime objects for assembly renderings 
    # @param self The object pointer
    def prepare(self):
        #Warm-up phase for rendering
        pass

    ## Set Camera 
    # Replace current camera 
    # @param self The object pointer
    # @param camera New camera 
    def set_camera(self, camera):
        pass

    ## Get Camera 
    # Get current camera 
    # @param self The object pointer
    def get_camera(self):
        pass
    
    ## Set resolution of the picture
    # @param self The object pointer
    # @param x Horizonal resolution 
    # @param y Vertical resolution 
    def set_resolution(self, x, y):
        pass

    ## Get current resolution of the picture
    # @param self The object pointer
    # @return tuple Return current resolution of the picture 
    def get_resolution(self):
        pass

    ## Set pixel size
    # By modify pixel size you can achieve zoom effect
    # Default size is 1.0
    # @param self The object pointer
    # @param size Size of the pixel 
    def set_pixel_size(self, size):
        pass

    ## Get pixel size
    # @param self The object pointer
    # @return float Return current size of the pixel 
    def get_pixel_size(self):
        pass

    ## Set Sampler 
    # Replace current sampler 
    # @param self The object pointer
    # @param sampler New sampler 
    def set_sampler(self, sampler):
        pass

    ## Get Sampler 
    # Get current sampler 
    # @param self The object pointer
    def get_sampler(self):
        pass

    ## Add material 
    # Add new material  
    # Material must have unique names
    # If material with specified name allready material is not added 
    # @param self The object pointer
    # @param name Name of the material 
    # @param material New material 
    def add_material(self, name, material):
        pass

    ## Add shape 
    # Add new shape  
    # Shape must have unique name
    # If shape with specified name allready exist shape is not added 
    # @param self The object pointer
    # @param name Name of the shape 
    # @param shape New shape 
    def add_shape(self, name, shape):
        pass

    ## Add light
    # Add new light
    # Light must have unique name
    # If light with specified name allready exist light is not added
    # @param self The object pointer
    # @param name Name of the light 
    # @param light New light 
    def add_light(self, name, light):
        pass

    ## Render one tile of the picture
    # To render whole picture you must repeatedly call this method
    # @param self The object pointer
    # @return bool False if not all tiles rendered True otherwise
    def render(self):
        pass

    ## Set material to shape 
    # If shape allready has material you will override that material
    # If material or shape doesn't exist method will return False 
    # @param self The object pointer
    # @param material_name Name of material  
    # @param shape_name Name of the shape  
    # @return bool True if all went succesfully otherwise False
    def set_material_to_shape(self, material_name, shape_name):
        pass

    ## Set rendering algorithm 
    # We can use different algorithm to render picture
    # Currently four algoritms are supported "raycast_asm", "raycast_py",
    # "path_tracer_asm", "path_tracer_py"
    # Default algorithm is "path_tracer_asm"
    # @param self The object pointer
    # @param algorithm Algorithm that is used for rendering 
    def set_rendering_algorithm(self, algorithm):
        pass

    ## Get picture that you rendered
    # @param self The object pointer
    # @param type Type of picture, FloatImage or IntegerImage 
    def get_picture(self, type):
        pass


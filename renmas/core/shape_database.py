
import renmas.utils 
import renmas

class ShapeDatabase:
    def __init__(self):
        # Data model for shape database
        # Solve how python objects can edit objects in dynamic array FIXME
        # for all shapes we need two dicts name:shape and shape:addr
        self.name_shapes = {}
        self.addr_shapes = {}
        self.lst_shapes = [] # list of objects - mybe we can avoid this! Think!!!
        # creation of list from dict is slow -- Think!!!
        # for every shape type we need one dynamic array
        self.dyn_arrays = {}

        # self dynamic arrays for intersection
        self.dyn_arrays_isect = {}
        self.prepared = False
        self.shapes_for_isect = []

    def add_shape(self, name, shape):
        # TODO solve the case when we have allready existing shape
        # Dynamic arrays in that case need to be updated
        self.name_shapes[name] = shape #TODO dynamic arrays need to be updated

        # Be very carefull - dynamic are do automatic resize by himself
        if type(shape) not in self.dyn_arrays:
            darr = renmas.utils.DynamicArray(shape.struct())
            darr.add_instance(shape.attributes())
            self.dyn_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self.dyn_arrays[type(shape)]
            idx = darr.num_objects()
            darr.add_instance(shape.attributes())

        self.addr_shapes[shape] = idx 
        self.lst_shapes.append(shape)

    # synchronize dynamic array with python objects - we must also need to remeber index 
    # where objects are placed in dynamic array
    # with this way we can let user to edit objects through GUI and synchonize this with assembler
    def _synchronize(self): # proposal - call before rendering starts
        pass

    def prepare_shapes(self):
        self.dyn_arrays_for_isect()
        self.shapes_for_isect = [self.grid]

    def isect_shapes(self):
        return self.shapes_for_isect

    def remove_shape(self, shape=None, name=None): #support for delete in dynamic array TODO
        pass

    def get_shape(self, name):
        return self.name_shapes.get(name, None)

    def obj_address(self, name=None, shape=None):
        if name is None and shape is None: return None
        sh = shape
        if name in self.name_shapes:
            sh = self.name_shapes[name]

        darr = self.dyn_arrays[type(sh)]
        addr = darr.get_addr() + self.addr_shapes[sh] * darr.obj_size() 
        return addr 

    def shapes(self):
        return self.lst_shapes

    def dyn_arrays_for_isect(self):
        if self.prepared: return self.dyn_arrays_isect 

        #prepare objects in agregate structures for fast intersection
        grid = renmas.shapes.Grid()
        grid.setup(self.shapes())
        self.grid = grid

        darr = renmas.utils.DynamicArray(grid.struct())
        darr.add_instance(grid.attributes())
        self.dyn_arrays_isect[type(grid)] = darr

        self.prepared = True
        return self.dyn_arrays_isect 
        

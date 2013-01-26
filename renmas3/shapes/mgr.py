
from tdasm import Tdasm
from ..base import DynamicArray, Vector3
from ..base.logger import log
from .bbox import BBox

class ShapeManager:
    def __init__(self):

        self._shape_names = {} #name:shape
        self._shape_addr = {} # shape:idx  - using index in dynamic array we can calculate address
        self._shape_arrays = {} # DynamicArrays for assembly rendering

    def names(self):
        return self._shape_names.keys()

    def shape(self, name):
        if name in self._shape_names:
            return self._shape_names[name]
        return None

    def shape_types(self):
        return self._shape_arrays.keys()

    def dynamic_array(self, shape_type):
        if shape_type not in self._shape_arrays:
            return None
        darr = self._shape_arrays[shape_type]
        return darr

    def _create_struct(self, shape):
        code = " #DATA " + shape.asm_struct() + """
        #CODE
        #END
        """
        mc = Tdasm().assemble(code)
        return mc.get_struct(shape.asm_struct_name())


    def add(self, name, shape):
        if name in self._shape_names:
            raise ValueError("Shape %s allready exist" % name)

        if shape in self._shape_addr:
            raise ValueError("Shape allready exist", shape)

        self._shape_names[name] = shape #name:shape
        # Tip: Be very carefull - dynamic arrays do automatic resize by himself
        if type(shape) not in self._shape_arrays:
            darr = DynamicArray(self._create_struct(shape))
            self._shape_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self._shape_arrays[type(shape)]
            idx = darr.num_objects()

        darr.add_instance(shape.attributes())
        self._shape_addr[shape] = idx 

    def remove(self, name): #TODO
        raise NotImplementedError()

    def update(self, shape):
        try:
            idx = self._shape_addr[shape]
            darr = self._shape_arrays[type(shape)]
            darr.edit_instance(idx, shape.attributes())
        except:
            log.info("Cannot update shape because shape doesn't exist!")

    def address_info(self, shape):
        idx = self._shape_addr.get(shape, None)
        if idx is None: 
            log.info("Cannot return address of Shape because shape doesn't exist!")
            return None

        darr = self._shape_arrays[type(shape)]
        addr = darr.address_info() + idx * darr.obj_size() 
        return addr

    def __iter__(self):
        for shape in self._shape_names.values():
            yield shape

    def bbox(self):
        p0 = Vector3(9999999.0, 9999999.0, 9999999.0)
        p1 = Vector3(-9999999.0, -9999999.0, -9999999.0)
        bb_min = BBox(p0, p1) 

        for shape in self:
            bbox = shape.bbox()

            if bbox.x0 < bb_min.x0: bb_min.x0 = bbox.x0
            if bbox.y0 < bb_min.y0: bb_min.y0 = bbox.y0
            if bbox.z0 < bb_min.z0: bb_min.z0 = bbox.z0

            if bbox.x1 > bb_min.x1: bb_min.x1 = bbox.x1
            if bbox.y1 > bb_min.y1: bb_min.y1 = bbox.y1
            if bbox.z1 > bb_min.z1: bb_min.z1 = bbox.z1

        return bb_min

    def __getstate__(self):
        d = {}
        d['shapes'] = self._shape_names
        return d

    def __setstate__(self, state):

        self._shape_names = {} 
        self._shape_addr = {} 
        self._shape_arrays = {}

        shapes = state['shapes']
        for name, shape in shapes.items():
            self.add(name, shape)



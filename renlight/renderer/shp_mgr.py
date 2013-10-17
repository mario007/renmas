
from renlight.sdl.arr import Array


class ShapeManager:
    def __init__(self):

        self._shape_names = {}  # name:shape
        self._shape_addr = {}  # shape:idx - using in calculation of address
        self._shape_arrays = {}  # DynamicArrays for assembly rendering

    def add(self, name, shape):
        if name in self._shape_names:
            raise ValueError("Shape %s allready exist" % name)

        if shape in self._shape_addr:
            raise ValueError("Shape allready exist", shape)

        self._shape_names[name] = shape
        if type(shape) not in self._shape_arrays:
            darr = Array(shape)
            self._shape_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self._shape_arrays[type(shape)]
            idx = len(darr)

        darr.append(shape)
        self._shape_addr[shape] = idx

    def shape_types(self):
        return self._shape_arrays.keys()

    def __iter__(self):
        for shape in self._shape_names.values():
            yield shape

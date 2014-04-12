
import math
from sdl import Vector3
from sdl.arr import ObjArray
from .sphere import Sphere


class ShapeManager:
    def __init__(self):

        self._shape_names = {}  # name:shape
        self._shape_addr = {}  # shape:idx - using in calculation of address
        self._shape_arrays = {}  # DynamicArrays for assembly rendering

        self._bbox = None

    def add(self, name, shape):
        if name in self._shape_names:
            raise ValueError("Shape %s allready exist" % name)

        if shape in self._shape_addr:
            raise ValueError("Shape allready exist", shape)

        self._shape_names[name] = shape
        if type(shape) not in self._shape_arrays:
            darr = ObjArray(shape)
            self._shape_arrays[type(shape)] = darr
            idx = 0
        else:
            darr = self._shape_arrays[type(shape)]
            idx = len(darr)

        darr.append(shape)
        self._shape_addr[shape] = idx
        self._update_bbox(shape)

    def update(self, shape):
        if shape not in self._shape_addr:
            raise ValueError("Shape doesn't exsist", shape)
        darr = self._shape_arrays[type(shape)]
        darr.update(shape)

    def shape_types(self):
        return self._shape_arrays.keys()

    def __iter__(self):
        for shape in self._shape_names.values():
            yield shape

    @property
    def bounding_sphere(self):
        if self._bbox is None:
            origin = Vector3(0.0, 0.0, 0.0)
            return Sphere(origin, radius=0.01, mat_idx=0)

        bbox = self._bbox
        dx = (bbox.x1 - bbox.x0) ** 2
        dy = (bbox.y1 - bbox.y0) ** 2
        dz = (bbox.z1 - bbox.z0) ** 2
        distance = math.sqrt(dx + dy + dz)
        radius = distance / 2.0

        ox = (bbox.x0 + bbox.x1) * 0.5
        oy = (bbox.y0 + bbox.y1) * 0.5
        oz = (bbox.z0 + bbox.z1) * 0.5
        origin = Vector3(ox, oy, oz)

        return Sphere(origin, radius=radius, mat_idx=0)

    def _update_bbox(self, shape):
        if self._bbox is None:
            self._bbox = shape.bbox()
            return

        bbox = shape.bbox()
        self._bbox.x0 = min(self._bbox.x0, bbox.x0)
        self._bbox.x1 = max(self._bbox.x1, bbox.x1)
        self._bbox.y0 = min(self._bbox.y0, bbox.y0)
        self._bbox.y1 = max(self._bbox.y1, bbox.y1)
        self._bbox.z0 = min(self._bbox.z0, bbox.z0)
        self._bbox.z1 = max(self._bbox.z1, bbox.z1)


from ..base import Ray, Vector3
from ..macros import create_assembler
from .hit import HitPoint
from .shape import Shape
from .bbox import BBox

class BaseMesh(Shape):

    def bbox(self):
        min_p, max_p = self.vb.bbox()
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1)

    def ntriangles(self):
        return self.tb.size()

    def bbox_triangle(self, idx):
        v = self.tb.get(idx)
        if v:
            return self.vb.bbox_triangle(v[0], v[1], v[2])
        return None


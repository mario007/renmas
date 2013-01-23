import random
from ..base import Vector3

class BBox:
    def __init__(self, p0, p1):
        self.x0 = p0.x
        self.y0 = p0.y
        self.z0 = p0.z
        self.x1 = p1.x
        self.y1 = p1.y
        self.z1 = p1.z

    def inside(self, p):
        return p.x >= self.x0 and p.x <= self.x1 and p.y >= self.y0\
                              and p.y <= self.y1 and p.z >= self.z0 and p.z <= self.z1  

    def isect(self, ray):
        ox = ray.origin.x
        oy = ray.origin.y
        oz = ray.origin.z
        dx = ray.dir.x
        dy = ray.dir.y
        dz = ray.dir.z

        a = 1.0 / dx
        if a >= 0:
            tx_min = (self.x0 - ox) * a
            tx_max = (self.x1 - ox) * a
        else:
            tx_min = (self.x1 - ox) * a
            tx_max = (self.x0 - ox) * a

        b = 1.0 / dy
        if b >= 0:
            ty_min = (self.y0 - oy) * b
            ty_max = (self.y1 - oy) * b
        else:
            ty_min = (self.y1 - oy) * b
            ty_max = (self.y0 - oy) * b

        c = 1.0 / dz
        if c >= 0:
            tz_min = (self.z0 - oz) * c
            tz_max = (self.z1 - oz) * c
        else:
            tz_min = (self.z1 - oz) * c
            tz_max = (self.z0 - oz) * c

        if tx_min > ty_min:
            t0 = tx_min
        else:
            t0 = ty_min

        if tz_min > t0:
            t0 = tz_min

        if tx_max < ty_max:
            t1 = tx_max
        else:
            t1 = ty_max

        if tz_max < t1:
            t1 = tz_max
        
        if t0 < t1 and t1 > 0.00001:
            if t0 > 0.00001:
                return t0
            return t1
        else:
            return False


def random_in_bbox(bbox):
    x = random.uniform(bbox.x0, bbox.x1)
    y = random.uniform(bbox.y0, bbox.y1)
    z = random.uniform(bbox.z0, bbox.z1)
    return Vector3(x, y, z)



from ..core import Vector3
from .hitpoint import HitPoint

class BBox:
    def __init__(self, p0, p1, material):
        self.x0 = p0.x
        self.y0 = p0.y
        self.z0 = p0.z
        self.x1 = p1.x
        self.y1 = p1.y
        self.z1 = p1.z
        self.material = material

    def inside(self, p):
        return p.x >= self.x0 and p.x <= self.x1 and p.y >= self.y0 and p.y <= self.y1 and p.z >= self.z0 and p.z <= self.z1  

    def intersect(self, ray): # repaire intersect min_dist FIXME
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
            if a >= 0.0: face_in = 0
            else: face_in = 3
        else:
            t0 = ty_min
            if b >= 0.0: face_in = 1
            else: face_in = 4

        if tz_min > t0:
            t0 = tz_min
            if c >= 0.0: face_in = 2
            else: face_in = 5

        if tx_max < ty_max:
            t1 = tx_max
            if a >= 0.0: face_out = 3
            else: face_out = 0
        else:
            t1 = ty_max
            if b >= 0.0: face_out = 4
            else: face_out = 1

        if tz_max < t1:
            t1 = tz_max
            if c >= 0.0: face_out = 5
            else: face_out = 2
        
        if t0 < t1 and t1 > 0.00001:
            if t0 > 0.00001:
                tmin = t0
                normal = self.get_normal(face_in)
            else:
                tmin = t1
                normal = self.get_normal(face_out)

            p = ray.origin + ray.dir * tmin
            return HitPoint(tmin, p, normal, self.material, ray)
        else:
            return False

    def get_normal(self, face):
        if face == 0: return Vector3(-1.0, 0.0, 0.0)
        elif face == 1: return Vector3(0.0, -1.0, 0.0)
        elif face == 2: return Vector3(0.0, 0.0, -1.0)
        elif face == 3: return Vector3(1.0, 0.0, 0.0)
        elif face == 4: return Vector3(0.0, 1.0, 0.0)
        elif face == 5: return Vector3(0.0, 0.0, 1.0)



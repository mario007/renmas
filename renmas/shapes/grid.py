
from tdasm import Tdasm, Runtime
import renmas.core
import renmas.utils as util
from renmas.shapes import BBox
from renmas.maths import Vector3
import math

def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))

def isect(ray, shapes):
    min_dist = 999999.0
    hit_point = None
    for s in shapes:
        hit = s.intersect(ray, min_dist)
        if hit is False: continue
        if hit.t < min_dist:
            min_dist = hit.t
            hit_point = hit
    return hit_point

class Grid:
    def __init__(self):
        self.bbox = None

    def setup(self):
        db_shapes = renmas.core.scene.shape_database

        p0 = Vector3(9999999.0, 9999999.0, 9999999.0)
        p1 = Vector3(-9999999.0, -9999999.0, -9999999.0)
        bb_min = BBox(p0, p1, None) 

        for shape in db_shapes.shapes():
            bbox = shape.get_bounding_box()

            if bbox.x0 < bb_min.x0: bb_min.x0 = bbox.x0
            if bbox.y0 < bb_min.y0: bb_min.y0 = bbox.y0
            if bbox.z0 < bb_min.z0: bb_min.z0 = bbox.z0

            if bbox.x1 > bb_min.x1: bb_min.x1 = bbox.x1
            if bbox.y1 > bb_min.y1: bb_min.y1 = bbox.y1
            if bbox.z1 > bb_min.z1: bb_min.z1 = bbox.z1

        self.bbox = bb_min

        
        num_shapes = len(db_shapes.shapes()) #FIXME when we incoorporate mesh
        wx = bb_min.x1 - bb_min.x0
        wy = bb_min.y1 - bb_min.y0
        wz = bb_min.z1 - bb_min.z0
        multiplier = 1.5 # about 8 times more cells than objects TODO test this!
        
        s = math.pow(wx * wy * wz / float(num_shapes), 0.333333)
        nx = int(multiplier * wx / s + 1)
        ny = int(multiplier * wy / s + 1)
        nz = int(multiplier * wz / s + 1)
        self.nx = nx
        self.ny = ny
        self.nz = nz

        num_cells = int(nx * ny * nz)
        print("nx=", nx, " ny=", ny, " nz=", nz)

        # every cell have referencs to objects that are in that cell
        self.cells = [] # we need to initialize list
        for c in range(num_cells):
            self.cells.append([])

        max_len = 0

        for shape in db_shapes.shapes():
            bbox = shape.get_bounding_box()
    
            ixmin = int(clamp((bbox.x0 - bb_min.x0) * nx / (bb_min.x1 - bb_min.x0), 0, nx - 1))
            iymin = int(clamp((bbox.y0 - bb_min.y0) * ny / (bb_min.y1 - bb_min.y0), 0, ny - 1))
            izmin = int(clamp((bbox.z0 - bb_min.z0) * nz / (bb_min.z1 - bb_min.z0), 0, nz - 1))
            ixmax = int(clamp((bbox.x1 - bb_min.x0) * nx / (bb_min.x1 - bb_min.x0), 0, nx - 1))
            iymax = int(clamp((bbox.y1 - bb_min.y0) * ny / (bb_min.y1 - bb_min.y0), 0, ny - 1))
            izmax = int(clamp((bbox.z1 - bb_min.z0) * nz / (bb_min.z1 - bb_min.z0), 0, nz - 1))
            #print("x = ", ixmin, ixmax)
            #print("y = ", iymin, iymax)
            #print("z = ", izmin, izmax)

            for k in range(izmin, izmax+1):
                for j in range(iymin, iymax+1):
                    for i in range(ixmin, ixmax+1):
                        idx = i + nx * j + nx * ny * k
                        self.cells[idx].append(shape)

                        duzina = len(self.cells[idx])
                        if duzina > max_len: max_len = duzina


        print("duzina", max_len)
        return None


    def intersect(self, ray, min_dist = 999999.0):
        ox = ray.origin.x
        oy = ray.origin.y
        oz = ray.origin.z
        dx = ray.dir.x
        dy = ray.dir.y
        dz = ray.dir.z

        x0 = self.bbox.x0
        y0 = self.bbox.y0
        z0 = self.bbox.z0
        x1 = self.bbox.x1
        y1 = self.bbox.y1
        z1 = self.bbox.z1

        a = 1.0 / dx
        if a >= 0:
            tx_min = (x0 - ox) * a
            tx_max = (x1 - ox) * a
        else:
            tx_min = (x1 - ox) * a
            tx_max = (x0 - ox) * a

        b = 1.0 / dy
        if b >= 0:
            ty_min = (y0 - oy) * b
            ty_max = (y1 - oy) * b
        else:
            ty_min = (y1 - oy) * b
            ty_max = (y0 - oy) * b

        c = 1.0 / dz
        if c >= 0:
            tz_min = (z0 - oz) * c
            tz_max = (z1 - oz) * c
        else:
            tz_min = (z1 - oz) * c
            tz_max = (z0 - oz) * c 

        if tx_min > ty_min: t0 = tx_min
        else: t0 = ty_min

        if tz_min > t0: t0 = tz_min

        if tx_max < ty_max: t1 = tx_max
        else: t1 = ty_max

        if tz_max < t1: t1 = tz_max

        if t0 > t1:
            return None #no intersection ocur

        if self.bbox.inside(ray.origin):
            ix = int(clamp((ox - x0) * self.nx / (x1 - x0), 0, self.nx - 1))
            iy = int(clamp((oy - y0) * self.ny / (y1 - y0), 0, self.ny - 1))
            iz = int(clamp((oz - z0) * self.nz / (z1 - z0), 0, self.nz - 1))
        else:
            p = ray.origin + ray.dir * t0 
            ix = int(clamp((p.x - x0) * self.nx / (x1 - x0), 0, self.nx - 1))
            iy = int(clamp((p.y - y0) * self.ny / (y1 - y0), 0, self.ny - 1))
            iz = int(clamp((p.z - z0) * self.nz / (z1 - z0), 0, self.nz - 1))

        dtx = (tx_max - tx_min) / self.nx
        dty = (ty_max - ty_min) / self.ny
        dtz = (tz_max - tz_min) / self.nz

        if dx > 0.0:
            tx_next = tx_min + (ix + 1) * dtx
            ix_step = 1
            ix_stop = self.nx
        else:
            tx_next = tx_min + (self.nx - ix) * dtx
            ix_step = -1
            ix_stop = -1
        if dx == 0.0:
            tx_next = 9999999.9999
            ix_step = -1
            ix_stop = -1

        if dy > 0.0:
            ty_next = ty_min + (iy + 1) * dty
            iy_step = 1
            iy_stop = self.ny
        else:
            ty_next = ty_min + (self.ny - iy) * dty
            iy_step = -1
            iy_stop = -1
        if dy == 0.0:
            ty_next = 9999999.9999
            iy_step = -1
            iy_stop = -1

        if dz > 0.0:
            tz_next = tz_min + (iz + 1) * dtz
            iz_step = 1
            iz_stop = self.nz
        else:
            tz_next = tz_min + (self.nz - iz) * dtz
            iz_step = -1
            iz_stop = -1
        if dz == 0.0:
            tz_next = 9999999.9999
            iz_step = -1
            iz_stop = -1

        while True:
            cell = self.cells[ix + self.nx * iy + self.nx * self.ny * iz]

            if tx_next < ty_next and tx_next < tz_next:
                hp = isect(ray, cell)
                if hp is not None and hp.t < tx_next:
                    return hp

                tx_next += dtx
                ix += ix_step
                if ix == ix_stop: return None
                
            else:
                if ty_next < tz_next:
                    hp = isect(ray, cell)
                    if hp is not None and hp.t < ty_next:
                        return hp

                    ty_next += dty
                    iy += iy_step
                    if iy == iy_stop: return None
                else:
                    hp = isect(ray, cell)
                    if hp is not None and hp.t < tz_next:
                        return hp

                    tz_next += dtz
                    iz += iz_step
                    if iz == iz_stop: return None
        return None



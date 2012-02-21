import math
import time
from array import array
import x86
from ..core import Vector3
from .bbox import BBox

def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))

class GridMesh:
    def __init__(self):
        self.bbox = None
        self.mesh = None

    def setup(self, mesh):
        self.mesh = mesh
        self.bbox = bbox = mesh.bbox()
        ntriangles = mesh.ntriangles() #get number of triangles
        wx = bbox.x1 - bbox.x0
        wy = bbox.y1 - bbox.y0
        wz = bbox.z1 - bbox.z0

        multiplier = 1.3 # about 8 times more cells than objects if multiplier is 2 TODO test this!
        s = math.pow(wx * wy * wz / float(ntriangles), 0.333333)

        self.nx = nx = int(multiplier * wx / s + 1)
        if nx > 256: self.nx = nx = 256 
        self.ny = ny = int(multiplier * wy / s + 1)
        if ny > 256: self.ny = ny = 256 
        self.nz = nz = int(multiplier * wz / s + 1)
        if nz > 256: self.nz = nz = 256 
        num_cells = int(nx * ny * nz)

        cells = [] # we need to initialize empty lists
        #for c in range(num_cells):
        #    cells.append([])
        for c in range(num_cells):
            cells.append(array("I"))
        
        # this is requierd for creation of array buffer
        max_len = 0 # max length in one cell
        num_arrays = 0
        num_objects = 0 

        nx1 = nx - 1
        ny1 = ny - 1
        nz1 = nz - 1
        nxwx = float(nx) / wx
        nywy = float(ny) / wy
        nzwz = float(nz) / wz
        nxny = nx * ny
         
        for idx_triangle in range(ntriangles):
            ob_min, ob_max = mesh.bbox_triangle(idx_triangle)

            ixmin = int((ob_min[0] - bbox.x0) * nxwx) 
            if ixmin > nx1: ixmin = nx1
            if ixmin < 0: ixmin = 0
            iymin = int((ob_min[1] - bbox.y0) * nywy)
            if iymin > ny1: iymin = ny1
            if iymin < 0: iymin = 0
            izmin = int((ob_min[2] - bbox.z0) * nzwz)
            if izmin > nz1: izmin = nz1
            if izmin < 0: izmin = 0
            ixmax = int((ob_max[0] - bbox.x0) * nxwx) 
            if ixmax > nx1: ixmax = nx1
            if ixmax < 0: ixmax = 0
            iymax = int((ob_max[1] - bbox.y0) * nywy)
            if iymax > ny1: iymax = ny1
            if iymax < 0: iymax = 0
            izmax = int((ob_max[2] - bbox.z0) * nzwz)
            if izmax > nz1: izmax = nz1
            if izmax < 0: izmax = 0

            #ixmin = int(clamp((ob_min[0] - bbox.x0) * nxwx, 0, nx1))
            #iymin = int(clamp((ob_min[1] - bbox.y0) * nywy, 0, ny1))
            #izmin = int(clamp((ob_min[2] - bbox.z0) * nzwz, 0, nz1))
            #ixmax = int(clamp((ob_max[0] - bbox.x0) * nxwx, 0, nx1))
            #iymax = int(clamp((ob_max[1] - bbox.y0) * nywy, 0, ny1))
            #izmax = int(clamp((ob_max[2] - bbox.z0) * nzwz, 0, nz1))

            stx = ixmin
            sty = iymin
            
            while True:
                ixmin = stx
                iymin = sty
                while True:
                    ixmin = stx
                    while True:
                        idx = ixmin + nx * iymin + nx * ny * izmin
                        cells[idx].append(idx_triangle)

                        duzina = len(cells[idx])
                        num_objects += 1
                        if duzina == 1: num_arrays += 1
                        if duzina > max_len: max_len = duzina

                        if ixmin == ixmax: break
                        ixmin += 1
                    if iymin == iymax: break
                    iymin += 1
                if izmin == izmax: break
                izmin += 1


            #for k in range(izmin, izmax+1):
            #    for j in range(iymin, iymax+1):
            #        for i in range(ixmin, ixmax+1):
            #            idx = i + nx * j + nx * ny * k
            #            lst_n.append(idx)
            #            cells[idx].append(idx_triangle)

            #            duzina = len(self.cells[idx])
            #            num_objects += 1
            #            if duzina == 1: num_arrays += 1
            #            if duzina > max_len: max_len = duzina

        self.max_length_in_cell = max_len
        self.num_objects = num_objects
        self.num_arrays = num_arrays

        self._create_grid(cells) 

        #self._compare_cells(cells, self.asm_cells, self.lin_array)
        cells = None #we hope that garbage collector will release memory 

    def _compare_seq(self, seq1, seq2):
        for i in range(len(seq1)):
            if seq1[i] != seq2[i]:
                raise ValueError("Error in Grid array!!!")

    def _compare_cells(self, cells, grid3d, arr):
        nx = self.nx
        ny = self.ny
        nz = self.nz
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    idx = i + nx * j + nx * ny * k
                    cell = cells[idx]
                    addr = grid3d.ptr() + idx * 4
                    idx_in_array = x86.GetUInt32(addr, 0, 0) 
                    if idx_in_array != 0:
                        addr = arr.ptr() + idx_in_array
                        ntri = x86.GetUInt32(addr, 0, 0)
                        triangles = x86.GetUInt32(addr+4, 0, ntri)
                        self._compare_seq(cell, triangles)


    def _create_grid(self, cells):
        # we must alocate memory for 3d grid and array
        nx = self.nx
        ny = self.ny
        nz = self.nz
        num_cells = int(nx * ny * nz)
        self.asm_cells = x86.MemData(num_cells*4)
        self.asm_cells.fill()
        self.lin_array = x86.MemData(self.num_arrays*4 + self.num_objects * 4 + 4) #we start of index[1] that why extra four bytes
        x86.SetUInt32(self.lin_array.ptr(), 0, 0)
        offset = 4 # offset is in bytes

        addr_cells = self.asm_cells.ptr()
        addr_arr = self.lin_array.ptr()
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    idx = i + nx * j + nx * ny * k
                    cell = cells[idx]
                    if len(cell) == 0:
                        pass
                    else:
                        adr = addr_cells + idx * 4
                        x86.SetUInt32(adr, offset, 0)

                        adr = addr_arr + offset
                        num = len(cell)
                        x86.SetUInt32(adr, num, 0)
                        offset += 4

                        x86.SetUInt32(adr+4, tuple(cell), 0)
                        offset = offset + len(cell) * 4


    def _show_info(self):
        print("Dimensions nx=", self.nx, " ny=", self.ny, "nz=", self.nz)
        print("Max length in cell = " , self.max_length_in_cell)
        print("Number of objects in Grid = ", self.num_objects)
        print("Number of requierd arrays = ", self.num_arrays)

        # we must alocate memory 3d grid and arrays
        print("Memory required for grid = ", self.nx * self.ny * self.nz * 4, " bytes")
        print("Memory required for array =", self.num_arrays*4 + self.num_objects*4 + 4, " bytes")

   
    def isect(self, ray, min_dist = 999999.0):
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
            return False #no intersection ocur

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
            #TODO both ways and test if garbage collector release memory!!!
            idx = ix + self.nx * iy + self.nx * self.ny * iz
            #cell = self.cells[ix + self.nx * iy + self.nx * self.ny * iz]
            addr = self.asm_cells.ptr() + idx * 4
            idx_in_array = x86.GetUInt32(addr, 0, 0) 
            if idx_in_array != 0:
                addr = self.lin_array.ptr() + idx_in_array
                ntri = x86.GetUInt32(addr, 0, 0)
                triangles = x86.GetUInt32(addr+4, 0, ntri)
            else:
                triangles = []

            if tx_next < ty_next and tx_next < tz_next:
                if len(triangles) > 0:
                    hp = self.mesh.isect_triangles(ray, triangles, min_dist)
                else:
                    hp = False 
                if hp and hp.t < tx_next:
                    return hp

                tx_next += dtx
                ix += ix_step
                if ix == ix_stop: return False 
                
            else:
                if ty_next < tz_next:
                    if len(triangles) > 0:
                        hp = self.mesh.isect_triangles(ray, triangles, min_dist)
                    else:
                        hp = False 
                    if hp and hp.t < ty_next:
                        return hp

                    ty_next += dty
                    iy += iy_step
                    if iy == iy_stop: return False 
                else:
                    if len(triangles) > 0:
                        hp = self.mesh.isect_triangles(ray, triangles, min_dist)
                    else:
                        hp = False 
                    if hp and hp.t < tz_next:
                        return hp

                    tz_next += dtz
                    iz += iz_step
                    if iz == iz_stop: return False 
        return False 


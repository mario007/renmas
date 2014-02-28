
import x86
from array import array
import time


def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))


class GridMesh:
    def __init__(self):
        self.bbox = None
        self.mesh = None

    def setup(self, mesh, performanse=False):

        self.mesh = mesh
        self.bbox = bbox = mesh.bbox()

        ntriangles = mesh.ntriangles()
        wx = bbox.x1 - bbox.x0
        wy = bbox.y1 - bbox.y0
        wz = bbox.z1 - bbox.z0

        multiplier = 1.3 # about 8 times more cells than objects if multiplier is 2
        s = pow(wx * wy * wz / float(ntriangles), 0.333333)

        MAX_WIDTH = 192
        self.nx = nx = int(multiplier * wx / s + 1)
        if nx > MAX_WIDTH:
            self.nx = nx = MAX_WIDTH
        self.ny = ny = int(multiplier * wy / s + 1)
        if ny > MAX_WIDTH:
            self.ny = ny = MAX_WIDTH
        self.nz = nz = int(multiplier * wz / s + 1)
        if nz > MAX_WIDTH:
            self.nz = nz = MAX_WIDTH
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
         
        nx_part = wx / float(nx)
        ny_part = wy / float(ny)
        nz_part = wz / float(nz)

        start = time.clock()

        for idx_triangle in range(ntriangles):
            ob_min, ob_max = mesh.bbox_triangle(idx_triangle)

            #NOTE this is faster than clamp which uses min, max
            ixmin = int((ob_min[0] - bbox.x0) * nxwx) 
            if ixmin > nx1:
                ixmin = nx1
            if ixmin < 0:
                ixmin = 0
            iymin = int((ob_min[1] - bbox.y0) * nywy)
            if iymin > ny1:
                iymin = ny1
            if iymin < 0:
                iymin = 0
            izmin = int((ob_min[2] - bbox.z0) * nzwz)
            if izmin > nz1:
                izmin = nz1
            if izmin < 0:
                izmin = 0
            ixmax = int((ob_max[0] - bbox.x0) * nxwx) 
            if ixmax > nx1:
                ixmax = nx1
            if ixmax < 0:
                ixmax = 0
            iymax = int((ob_max[1] - bbox.y0) * nywy)
            if iymax > ny1:
                iymax = ny1
            if iymax < 0:
                iymax = 0
            izmax = int((ob_max[2] - bbox.z0) * nzwz)
            if izmax > nz1:
                izmax = nz1
            if izmax < 0:
                izmax = 0

            stx = ixmin
            sty = iymin
            
            if performanse:
                v0, v1, v2 = mesh.get_indices(idx_triangle)
                p0 = mesh.get_point(v0)
                p1 = mesh.get_point(v1)
                p2 = mesh.get_point(v2)

            #NOTE while is faster than for and this is speed critical code
            
            while True:
                ixmin = stx
                iymin = sty
                while True:
                    ixmin = stx
                    while True:
                        ret = 1 
                        if performanse:
                            start_x = ixmin * nx_part + bbox.x0
                            end_x = (ixmin + 1) * nx_part + bbox.x0
                            start_y = iymin * ny_part  + bbox.y0
                            end_y = (iymin + 1) * ny_part + bbox.y0
                            start_z = izmin * nz_part + bbox.z0
                            end_z = (izmin + 1) * nz_part + bbox.z0
                            box_center = ((start_x+end_x)/2.0, (start_y+end_y)/2.0, (start_z+end_z)/2.0)
                            half_size = ((end_x-start_x)/2.0, (end_y-start_y)/2.0, (end_z-start_z)/2.0)
                            ret = tri_box_overlap(box_center, half_size, (p0,p1,p2))

                        if ret == 1:
                            idx = ixmin + nx * iymin + nx * ny * izmin
                            cells[idx].append(idx_triangle)

                            duzina = len(cells[idx])
                            num_objects += 1
                            if duzina == 1:
                                num_arrays += 1
                            if duzina > max_len:
                                max_len = duzina

                        if ixmin == ixmax: break
                        ixmin += 1
                    if iymin == iymax: break
                    iymin += 1
                if izmin == izmax: break
                izmin += 1

        elapsed = time.clock() - start
        #print("While loop took %f seconds" % elapsed)

        self.max_length_in_cell = max_len
        self.num_objects = num_objects
        self.num_arrays = num_arrays

        self._create_grid(cells) 

        #self._compare_cells(cells, self.asm_cells, self.lin_array)
        cells = None  # we hope that garbage collector will release memory 

    def _create_grid(self, cells):
        # we must alocate memory for 3d grid and array
        nx = self.nx
        ny = self.ny
        nz = self.nz
        num_cells = int(nx * ny * nz)
        self.asm_cells = x86.MemData(num_cells*4)
        self.asm_cells.fill() #fill array(3d grid) with zero

        #NOTE we start of index[1] that why extra four bytes
        self.lin_array = x86.MemData(self.num_arrays * 4 + self.num_objects * 4 + 4)
        x86.SetUInt32(self.lin_array.ptr(), 0, 0)
        offset = 4  # offset is in bytes

        addr_cells = self.asm_cells.ptr()
        addr_arr = self.lin_array.ptr()
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    idx = i + nx * j + nx * ny * k
                    cell = cells[idx]
                    if len(cell) != 0:
                        adr = addr_cells + idx * 4
                        x86.SetUInt32(adr, offset, 0)

                        adr = addr_arr + offset
                        num = len(cell)
                        x86.SetUInt32(adr, num, 0)
                        offset += 4

                        x86.SetUInt32(adr + 4, tuple(cell), 0)
                        offset = offset + len(cell) * 4


    @classmethod
    def isect_shader_code(cls, isect_triangles):
        code = """
tmp_hitpoint = HitPoint()
#TODO handling NaN ray-box intersection

origin = ray.origin
direction = ray.direction
bbox_min = mesh.bbox_min
bbox_max = mesh.bbox_max


inv_dir = (1.0, 1.0, 1.0) / direction
tbot = (bbox_min - origin) * inv_dir
ttop = (bbox_max - origin) * inv_dir

tmin = min(ttop, tbot)
tmax = max(ttop, tbot)

tmp = max(tmin[0], tmin[1])
tmp2 = max(tmin[0], tmin[2])
largest_tmin = max(tmp, tmp2)

tmp = min(tmax[0], tmax[1])
tmp2 = min(tmax[0], tmax[2])
smallest_tmax = min(tmp, tmp2)

if largest_tmin > smallest_tmax:
    return 0

ox = ray.direction * largest_tmin  + origin
if origin[0] > bbox_min[0]: # test if origin is bbox
    if origin[0] < bbox_max[0]:
        if origin[1] > bbox_min[1]:
            if origin[1] < bbox_max[1]:
                if origin[2] > bbox_min[2]:
                    if origin[2] < bbox_max[2]:
                        ox = origin

nx = float(mesh.nx)
ny = float(mesh.ny)
nz = float(mesh.nz)
grid_width = float3(nx, ny, nz)

ixyz = (ox - bbox_min) * grid_width / (bbox_max - bbox_min)
nxyz = grid_width - (1.0, 1.0, 1.0)
ixyz = min(nxyz, ixyz)
tmp = float3(0.0, 0.0, 0.0)
ixyz = max(tmp, ixyz)

dtxyz = (tmax - tmin) / grid_width

if direction[0] > 0.0:
    tx_next = tmin[0] + (ixyz[0] + 1.0) * dtxyz[0]
    ix_step = 1
    ix_stop = mesh.nx
else:
    tx_next = tmin[0] + (float(mesh.nx) - ixyz[0]) * dtxyz[0]
    ix_step = -1
    ix_stop = -1
if direction[0] == 0.0:
    tx_next = 9999999.9999
    ix_step = -1
    ix_stop = -1

if direction[1] > 0.0:
    ty_next = tmin[1] + (ixyz[1] + 1.0) * dtxyz[1]
    iy_step = 1
    iy_stop = mesh.ny
else:
    ty_next = tmin[1] + (float(mesh.ny) - ixyz[1]) * dtxyz[1]
    iy_step = -1
    iy_stop = -1
if direction[1] == 0.0:
    ty_next = 9999999.9999
    iy_step = -1
    iy_stop = -1

if direction[2] > 0.0:
    tz_next = tmin[2] + (ixyz[2] + 1.0) * dtxyz[2]
    iz_step = 1
    iz_stop = mesh.nz
else:
    tz_next = tmin[2] + (float(mesh.nz) - ixyz[2]) * dtxyz[2]
    iz_step = -1
    iz_stop = -1
if direction[2] == 0.0:
    tz_next = 9999999.9999
    iz_step = -1
    iz_stop = -1

nx = mesh.nx
ny = mesh.ny
ix = int(ixyz[0])
iy = int(ixyz[1])
iz = int(ixyz[2])

while 1:
    idx = ix + nx * iy + nx * ny * iz
    idx = idx * 4  # each cell is 4 bytes
    addr = mesh.cells + idx
    idx_in_array = resolve(addr, int)

    tmp = min(tx_next, ty_next)
    tmp = min(tmp, tz_next)

    if tmp == tx_next:
        ret = 0
        if idx_in_array > 0:
            ret = %s(ray, mesh, idx_in_array, min_dist, tmp_hitpoint)
        if ret == 1:
            if tmp_hitpoint.t < tx_next:
                hitpoint.t = tmp_hitpoint.t
                hitpoint.normal = tmp_hitpoint.normal
                hitpoint.hit = tmp_hitpoint.hit
                hitpoint.u = tmp_hitpoint.u
                hitpoint.v = tmp_hitpoint.v
                hitpoint.mat_idx = mesh.mat_idx
                return 1

        tx_next = tx_next + dtxyz[0]
        ix = ix + ix_step
        if ix == ix_stop:
            return 0

    if tmp == ty_next:
        ret = 0
        if idx_in_array > 0:
            ret = %s(ray, mesh, idx_in_array, min_dist, tmp_hitpoint)
        if ret == 1:
            if tmp_hitpoint.t < ty_next:
                hitpoint.t = tmp_hitpoint.t
                hitpoint.normal = tmp_hitpoint.normal
                hitpoint.hit = tmp_hitpoint.hit
                hitpoint.u = tmp_hitpoint.u
                hitpoint.v = tmp_hitpoint.v
                hitpoint.mat_idx = mesh.mat_idx
                return 1

        ty_next = ty_next + dtxyz[1]
        iy = iy + iy_step
        if iy == iy_stop:
            return 0

    if tmp == tz_next:
        ret = 0
        if idx_in_array > 0:
            ret = %s(ray, mesh, idx_in_array, min_dist, tmp_hitpoint)
        if ret == 1:
            if tmp_hitpoint.t < tz_next:
                hitpoint.t = tmp_hitpoint.t
                hitpoint.normal = tmp_hitpoint.normal
                hitpoint.hit = tmp_hitpoint.hit
                hitpoint.u = tmp_hitpoint.u
                hitpoint.v = tmp_hitpoint.v
                hitpoint.mat_idx = mesh.mat_idx
                return 1

        tz_next = tz_next + dtxyz[2]
        iz = iz + iz_step
        if iz == iz_stop:
            return 0

return 0
        """ % (isect_triangles, isect_triangles, isect_triangles)
        return code

    def isect(self, ray, min_dist = 999999.0):
        ox = ray.origin.x
        oy = ray.origin.y
        oz = ray.origin.z
        dx = ray.direction.x
        dy = ray.direction.y
        dz = ray.direction.z

        x0 = self.bbox.x0
        y0 = self.bbox.y0
        z0 = self.bbox.z0
        x1 = self.bbox.x1
        y1 = self.bbox.y1
        z1 = self.bbox.z1

        if dx == 0.0: dx = 0.0000001
        a = 1.0 / dx
        if a >= 0:
            tx_min = (x0 - ox) * a
            tx_max = (x1 - ox) * a
        else:
            tx_min = (x1 - ox) * a
            tx_max = (x0 - ox) * a
        
        if dy == 0.0: dy = 0.0000001
        b = 1.0 / dy
        if b >= 0:
            ty_min = (y0 - oy) * b
            ty_max = (y1 - oy) * b
        else:
            ty_min = (y1 - oy) * b
            ty_max = (y0 - oy) * b

        if dz == 0.0: dz = 0.0000001
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
            p = ray.origin + ray.direction * t0 
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
            idx = ix + self.nx * iy + self.nx * self.ny * iz
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
                if ix == ix_stop:
                    return False 
                
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
                    if iy == iy_stop:
                        return False 
                else:
                    if len(triangles) > 0:
                        hp = self.mesh.isect_triangles(ray, triangles, min_dist)
                    else:
                        hp = False 
                    if hp and hp.t < tz_next:
                        return hp

                    tz_next += dtz
                    iz += iz_step
                    if iz == iz_stop:
                        return False 
        return False 

    @classmethod
    def isect_shader_b_code(cls, isect_triangles):
        code = """
#TODO handling NaN ray-box intersection

origin = ray.origin
direction = ray.direction
bbox_min = mesh.bbox_min
bbox_max = mesh.bbox_max


inv_dir = (1.0, 1.0, 1.0) / direction
tbot = (bbox_min - origin) * inv_dir
ttop = (bbox_max - origin) * inv_dir

tmin = min(ttop, tbot)
tmax = max(ttop, tbot)

tmp = max(tmin[0], tmin[1])
tmp2 = max(tmin[0], tmin[2])
largest_tmin = max(tmp, tmp2)

tmp = min(tmax[0], tmax[1])
tmp2 = min(tmax[0], tmax[2])
smallest_tmax = min(tmp, tmp2)

if largest_tmin > smallest_tmax:
    return 0

ox = ray.direction * largest_tmin  + origin
if origin[0] > bbox_min[0]: # test if origin is bbox
    if origin[0] < bbox_max[0]:
        if origin[1] > bbox_min[1]:
            if origin[1] < bbox_max[1]:
                if origin[2] > bbox_min[2]:
                    if origin[2] < bbox_max[2]:
                        ox = origin

nx = float(mesh.nx)
ny = float(mesh.ny)
nz = float(mesh.nz)
grid_width = float3(nx, ny, nz)

ixyz = (ox - bbox_min) * grid_width / (bbox_max - bbox_min)
nxyz = grid_width - (1.0, 1.0, 1.0)
ixyz = min(nxyz, ixyz)
tmp = float3(0.0, 0.0, 0.0)
ixyz = max(tmp, ixyz)

dtxyz = (tmax - tmin) / grid_width

if direction[0] > 0.0:
    tx_next = tmin[0] + (ixyz[0] + 1.0) * dtxyz[0]
    ix_step = 1
    ix_stop = mesh.nx
else:
    tx_next = tmin[0] + (float(mesh.nx) - ixyz[0]) * dtxyz[0]
    ix_step = -1
    ix_stop = -1
if direction[0] == 0.0:
    tx_next = 9999999.9999
    ix_step = -1
    ix_stop = -1

if direction[1] > 0.0:
    ty_next = tmin[1] + (ixyz[1] + 1.0) * dtxyz[1]
    iy_step = 1
    iy_stop = mesh.ny
else:
    ty_next = tmin[1] + (float(mesh.ny) - ixyz[1]) * dtxyz[1]
    iy_step = -1
    iy_stop = -1
if direction[1] == 0.0:
    ty_next = 9999999.9999
    iy_step = -1
    iy_stop = -1

if direction[2] > 0.0:
    tz_next = tmin[2] + (ixyz[2] + 1.0) * dtxyz[2]
    iz_step = 1
    iz_stop = mesh.nz
else:
    tz_next = tmin[2] + (float(mesh.nz) - ixyz[2]) * dtxyz[2]
    iz_step = -1
    iz_stop = -1
if direction[2] == 0.0:
    tz_next = 9999999.9999
    iz_step = -1
    iz_stop = -1

nx = mesh.nx
ny = mesh.ny
ix = int(ixyz[0])
iy = int(ixyz[1])
iz = int(ixyz[2])

while 1:
    idx = ix + nx * iy + nx * ny * iz
    idx = idx * 4  # each cell is 4 bytes
    addr = mesh.cells + idx
    idx_in_array = resolve(addr, int)

    tmp = min(tx_next, ty_next)
    tmp = min(tmp, tz_next)

    if tmp == tx_next:
        ret = 0
        if idx_in_array > 0:
            ret = %s(ray, mesh, idx_in_array, min_dist)
        if ret == 1:
            return 1

        tx_next = tx_next + dtxyz[0]
        ix = ix + ix_step
        if ix == ix_stop:
            return 0

    if tmp == ty_next:
        ret = 0
        if idx_in_array > 0:
            ret = %s(ray, mesh, idx_in_array, min_dist)
        if ret == 1:
            return 1

        ty_next = ty_next + dtxyz[1]
        iy = iy + iy_step
        if iy == iy_stop:
            return 0

    if tmp == tz_next:
        ret = 0
        if idx_in_array > 0:
            ret = %s(ray, mesh, idx_in_array, min_dist)
        if ret == 1:
            return 1

        tz_next = tz_next + dtxyz[2]
        iz = iz + iz_step
        if iz == iz_stop:
            return 0

return 0
        """ % (isect_triangles, isect_triangles, isect_triangles)
        return code


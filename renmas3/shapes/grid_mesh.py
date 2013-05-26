
import math
from array import array
import x86
from ..base import Vector3
from .bbox import BBox
import renmas3.switch as proc

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
        #if nx > 256: self.nx = nx = 256 
        if nx > 192: self.nx = nx = 192 
        self.ny = ny = int(multiplier * wy / s + 1)
        if ny > 192: self.ny = ny = 192 
        #if ny > 256: self.ny = ny = 256 
        self.nz = nz = int(multiplier * wz / s + 1)
        #if nz > 256: self.nz = nz = 256 
        if nz > 192: self.nz = nz = 192 
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

        #self._create_grid(cells) 
        print (cells)

        #self._compare_cells(cells, self.asm_cells, self.lin_array)
        cells = None #we hope that garbage collector will release memory 

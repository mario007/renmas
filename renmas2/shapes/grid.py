
import math
import time
from array import array
import x86
from ..core import Vector3
from .bbox import BBox
import renmas2.switch as proc

def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))

class Grid:
    def __init__(self):
        pass

    def _bbox(self, shapes):
        p0 = Vector3(9999999.0, 9999999.0, 9999999.0)
        p1 = Vector3(-9999999.0, -9999999.0, -9999999.0)
        bb_min = BBox(p0, p1, None) 

        for shape in shapes:
            if hasattr(shape, "_grid"):
                bbox = shape._grid.bbox
            else:
                bbox = shape.bbox()

            if bbox.x0 < bb_min.x0: bb_min.x0 = bbox.x0
            if bbox.y0 < bb_min.y0: bb_min.y0 = bbox.y0
            if bbox.z0 < bb_min.z0: bb_min.z0 = bbox.z0

            if bbox.x1 > bb_min.x1: bb_min.x1 = bbox.x1
            if bbox.y1 > bb_min.y1: bb_min.y1 = bbox.y1
            if bbox.z1 > bb_min.z1: bb_min.z1 = bbox.z1

        self.bbox = bb_min

    def setup(self, shapes):
        self._bbox(shapes)
        bbox = self.bbox
        wx = bbox.x1 - bbox.x0
        wy = bbox.y1 - bbox.y0
        wz = bbox.z1 - bbox.z0

        multiplier = 1.3 # about 8 times more cells than objects if multiplier is 2 TODO test this!
        s = math.pow(wx * wy * wz / float(len(shapes)), 0.333333)

        self.nx = nx = int(multiplier * wx / s + 1)
        if nx > 192: self.nx = nx = 192 
        self.ny = ny = int(multiplier * wy / s + 1)
        if ny > 192: self.ny = ny = 192 
        self.nz = nz = int(multiplier * wz / s + 1)
        if nz > 192: self.nz = nz = 192 
        num_cells = int(nx * ny * nz)
        
        self.cells = cells = [] # we need to initialize empty lists
        for c in range(num_cells):
            cells.append([])
        
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

        for shape in shapes:
            if hasattr(shape, "_grid"):
                bbox1 = shape._grid.bbox
            else:
                bbox1 = shape.bbox()

            ixmin = int(clamp((bbox1.x0 - bbox.x0) * nxwx, 0, nx1))
            iymin = int(clamp((bbox1.y0 - bbox.y0) * nywy, 0, ny1))
            izmin = int(clamp((bbox1.z0 - bbox.z0) * nzwz, 0, nz1))
            ixmax = int(clamp((bbox1.x1 - bbox.x0) * nxwx, 0, nx1))
            iymax = int(clamp((bbox1.y1 - bbox.y0) * nywy, 0, ny1))
            izmax = int(clamp((bbox1.z1 - bbox.z0) * nzwz, 0, nz1))

            for k in range(izmin, izmax+1):
                for j in range(iymin, iymax+1):
                    for i in range(ixmin, ixmax+1):
                        idx = i + nx * j + nx * ny * k
                        cells[idx].append(shape)

                        duzina = len(self.cells[idx])
                        num_objects += 1
                        if duzina == 1: num_arrays += 1
                        if duzina > max_len: max_len = duzina


        self.max_length_in_cell = max_len
        self.num_objects = num_objects
        self.num_arrays = num_arrays
        print(max_len, num_objects, num_arrays)

    #linear array looks like nobjects:{ptr_obj, ptr_func}
    def _create_grid(self, runtimes, intersector, visibility=False):
        # we must alocate memory for 3d grid and array
        cells = self.cells
        nx = self.nx
        ny = self.ny
        nz = self.nz
        num_cells = int(nx * ny * nz)
        if visibility:
            self.asm_cells_b = x86.MemData(num_cells*4)
            self.asm_cells_b.fill()
            self.lin_arrays_b = {}
        else:
            self.asm_cells = x86.MemData(num_cells*4)
            self.asm_cells.fill()
            self.lin_arrays = {}

        for r in runtimes:
            if visibility:
                self.lin_arrays_b[r] = x86.MemData(self.num_arrays*4 + self.num_objects * 8 + 4) #we start of index[1] that why extra four bytes
                x86.SetUInt32(self.lin_arrays_b[r].ptr(), 0, 0)
            else:
                self.lin_arrays_b = {}
                self.lin_arrays[r] = x86.MemData(self.num_arrays*4 + self.num_objects * 8 + 4) #we start of index[1] that why extra four bytes
                x86.SetUInt32(self.lin_arrays[r].ptr(), 0, 0)
        offset = 4 # offset is in bytes
        
        if visibility:
            addr_cells = self.asm_cells_b.ptr()
        else:
            addr_cells = self.asm_cells.ptr()

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

                        for r in runtimes:
                            if visibility:
                                addr_arr = self.lin_arrays_b[r].ptr()
                            else:
                                addr_arr = self.lin_arrays[r].ptr()

                            adr = addr_arr + offset
                            num = len(cell)
                            x86.SetUInt32(adr, num, 0)
                            x86.SetUInt32(adr+4, self._get_ptrs_obj_func(cell, r, intersector, visibility), 0)
                        offset = offset + len(cell) * 8 + 4

    def _get_ptrs_obj_func(self, shapes, runtime, intersector, visibility):
        adrs = []
        for s in shapes:
            adrs.append(intersector.address_off(s))
            if visibility:
                adrs.append(runtime.address_label(s.name() + "_intersect_bool"))
            else:
                adrs.append(runtime.address_label(s.name() + "_intersect"))
        return tuple(adrs)

    def _load_isect_functions(self, runtimes, assembler, structures, dyn_arrays, visibility=False):
        for key, value in dyn_arrays.items():
            if visibility:
                key.isect_asm_b(runtimes, key.name() + "_intersect_bool", assembler, structures)
            else:
                key.isect_asm(runtimes, key.name() + "_intersect", assembler, structures)

    def isect_shapes(self, ray, shapes):
        min_dist = 999999.0
        hit_point = False 
        for s in shapes:
            hit = s.isect(ray, min_dist)
            if hit is False: continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def isect_b(self, ray, min_dist=999999.0): #ray direction must be normalized
        hp = self.isect(ray, min_dist)
        if hp:
            return hp.t
        return hp

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

        if dx == 0.0: dx = 0.00001
        a = 1.0 / dx
        if a >= 0:
            tx_min = (x0 - ox) * a
            tx_max = (x1 - ox) * a
        else:
            tx_min = (x1 - ox) * a
            tx_max = (x0 - ox) * a

        if dy == 0.0: dy = 0.00001 
        b = 1.0 / dy
        if b >= 0:
            ty_min = (y0 - oy) * b
            ty_max = (y1 - oy) * b
        else:
            ty_min = (y1 - oy) * b
            ty_max = (y0 - oy) * b

        if dz == 0.0: dz = 0.00001 
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
            cell = self.cells[ix + self.nx * iy + self.nx * self.ny * iz]

            if tx_next < ty_next and tx_next < tz_next:
                hp = self.isect_shapes(ray, cell)
                if hp and hp.t < tx_next:
                    return hp

                tx_next += dtx
                ix += ix_step
                if ix == ix_stop: return False 
                
            else:
                if ty_next < tz_next:
                    hp = self.isect_shapes(ray, cell)
                    if hp and hp.t < ty_next:
                        return hp

                    ty_next += dty
                    iy += iy_step
                    if iy == iy_stop: return False 
                else:
                    hp = self.isect_shapes(ray, cell)
                    if hp and hp.t < tz_next:
                        return hp

                    tz_next += dtz
                    iz += iz_step
                    if iz == iz_stop: return False 
        return False 

    def isect_asm_b(self, runtimes, label, assembler, structures, dyn_arrays, intersector):
        self._load_isect_functions(runtimes, assembler, structures, dyn_arrays, True)
        self._create_grid(runtimes, intersector, True)
        label_ray_shapes = "ray_objects_intersections_bool"
        self.isect_ray_shapes_b(runtimes, label_ray_shapes, assembler, structures)

        code = """
            #DATA
        """
        code += structures.structs(('ray',)) + """
        uint32 ray_ptr
        float one[4] = 1.0, 1.0, 1.0, 0.0
        float zero[4] = 0.0, 0.0, 0.0, 0.0
        uint32 ones = 0xFFFFFFFF
        int32 ixyz[4]
        float dtxyz[4]
        int32 ix_step, iy_step, iz_step
        int32 ix_stop, iy_stop, iz_stop
        float tx_next, ty_next, tz_next
        float khuge = 999999.999
        float minimum_distance = 999999.0
        int32 n[4]

        uint32 grid_ptr
        uint32 arr_ptr
        float bbox_min[4]
        float bbox_max[4]
        float nbox_width[4]
        float n_1[4]
        float one_overn[4]
        uint32 grid_size[4]
        
        #CODE
        """
        code += " global " + label + ":\n" + """
            mov dword [ray_ptr], eax
            mov ebp, dword [khuge]
            mov dword [minimum_distance], ebp
        """
        #TODO --- think if ray direction has zero component -- put some epsilon!!!
        code += """
            macro eq128 xmm0 = one / eax.ray.dir
        """
        code += "macro eq128 xmm1 = bbox_min\n"
        code += "macro eq128 xmm2 = bbox_max\n"
        code += """

            macro eq128 xmm1 = xmm1 - eax.ray.origin
            macro eq128 xmm1 = xmm1 * xmm0

            macro eq128 xmm2 = xmm2 - eax.ray.origin
            macro eq128 xmm2 = xmm2 * xmm0

            macro eq128 xmm3 = xmm1
            macro eq128 xmm4 = xmm2

            ; tx_min, ty_min, tz_min
            macro call minps xmm3, xmm2
            ; tx_max, ty_max, tz_max
            macro call maxps xmm4, xmm1

            macro broadcast xmm5 = xmm3[1]
            macro call maxss xmm5, xmm3
            macro broadcast xmm6 = xmm3[2]
            ;t0
            macro call maxss xmm6, xmm5

            macro broadcast xmm5 = xmm4[1]
            macro call minss xmm5, xmm4
            macro broadcast xmm7 = xmm4[2]
            ;t1
            macro call minss xmm7, xmm5
            
            macro if xmm7 > xmm6 goto next_section
            mov eax, 0 ;no intersection ocur
            ret
            
            ;now we must check this if self.bbox.inside(ray.origin) 
            next_section:
            macro eq128 xmm0 = eax.ray.origin
            macro eq128 xmm2 = xmm0
        """
        code += "macro eq128 xmm1 = bbox_max\n"
        code += """
            ; le - less or equal (xmm0 <= xmm1)
            macro call cmpps xmm0, xmm1, 2
        """
        code += "macro eq128 xmm5 = bbox_min\n"
        code += """
            macro call cmpps xmm5, xmm2, 2 
            macro call andps xmm0, xmm5
            macro broadcast xmm1 = xmm0[1]
            macro broadcast xmm2 = xmm0[2]
            macro call andps xmm0, xmm1
            macro call andps xmm0, xmm2
        """
        if proc.AVX:
            code += "vcomiss xmm0, dword [ones] \n"
        else:
            code += "comiss xmm0, dword [ones] \n"

        code += """
            jz point_inside ; point is inside bbox

            macro eq128 xmm0 = eax.ray.dir * xmm6 + eax.ray.origin
            jmp next_section2

            point_inside:
            macro eq128 xmm0 = eax.ray.origin

            next_section2:
        """
        code +=  "macro eq128 xmm0 = xmm0 - bbox_min\n"
        code +=  "macro eq128 xmm0 = xmm0 * nbox_width\n"
        code +=  "macro eq128 xmm2 = n_1\n"
        code += """
            macro call zero xmm1
            macro call minps xmm0, xmm2
            macro call maxps xmm0, xmm1
            ; ix, iy, iz
        """
        if proc.AVX:
            code += """
            vcvttps2dq xmm1, xmm0
            vcvtdq2ps xmm0, xmm1
            """
        else:
            code += """
            cvttps2dq xmm1, xmm0
            cvtdq2ps xmm0, xmm1
            """
        code += """
            macro eq128 ixyz = xmm1 {xmm7}
            macro eq128 xmm5 = xmm4
            macro eq128 xmm5 = xmm5 - xmm3
        """
        code += "macro eq128 xmm5 = xmm5 * one_overn\n"
        code += """
            ; xmm5 = dtx, dty, dtz
            macro eq128 dtxyz = xmm5 {xmm7}

            ;tx_next = tx_min + (ix + 1) * dtx
            ;tx_next = tx_min + (self.nx - ix) * dtx
            macro eq128 xmm6 = one
            macro eq128 xmm6 = xmm6 + xmm0
            macro eq128 xmm6 = xmm6 * xmm5
            macro eq128 xmm6 = xmm6 + xmm3
        """
        code += "macro eq128 xmm7 = grid_size\n"
        code += """
            macro eq128 n = xmm7 {xmm0}
            macro eq128 xmm2 = xmm7
            macro call int_to_float xmm7, xmm7
            macro eq128 xmm7 = xmm7 - xmm0
            macro eq128 xmm7 = xmm7 * xmm5
            macro eq128 xmm7 = xmm7 + xmm3

            macro eq128 xmm0 = eax.ray.dir
        """
        if proc.AVX:
            code += "vcomiss xmm0, dword [zero]\n" 
        else:
            code += "comiss xmm0, dword [zero]\n" 
        code += """
            jz _equal1
            jnc _greater1

            mov dword [ix_step], -1
            mov dword [ix_stop], -1
            macro eq32 tx_next = xmm7 {xmm0}

            jmp _next_dx

            _greater1:
            mov dword [ix_step], 1
            macro eq32 ix_stop = xmm2 {xmm0}
            macro eq32 tx_next = xmm6 {xmm0}
            jmp _next_dx

            _equal1:
            mov ebp, dword [khuge]
            mov dword [ix_step], -1
            mov dword [ix_stop], -1
            mov dword [tx_next], ebp 

            _next_dx:
            macro broadcast xmm1 = xmm0[1]
        """
        if proc.AVX:
            code += "vcomiss xmm1, dword [zero]\n" 
        else:
            code += "comiss xmm1, dword [zero]\n" 
        code += """
            jz _equal2
            jnc _greater2

            mov dword [iy_step], -1
            mov dword [iy_stop], -1
            macro broadcast xmm5 = xmm7[1]
            macro eq32 ty_next = xmm5 {xmm0}

            jmp _next_dx2

            _greater2:
            mov dword [iy_step], 1
            macro broadcast xmm4 = xmm2[1]
            macro eq32 iy_stop = xmm4 {xmm0}
            macro broadcast xmm5 = xmm6[1]
            macro eq32 ty_next = xmm5 {xmm0}
            jmp _next_dx2

            _equal2:
            mov ebp, dword [khuge]
            mov dword [iy_step], -1
            mov dword [iy_stop], -1
            mov dword [ty_next], ebp 

            _next_dx2:
            macro broadcast xmm1 = xmm0[2]
        """
        if proc.AVX:
            code += "vcomiss xmm1, dword [zero]\n" 
        else:
            code += "comiss xmm1, dword [zero]\n" 
        code += """
            jz _equal3
            jnc _greater3

            mov dword [iz_step], -1
            mov dword [iz_stop], -1
            macro broadcast xmm5 = xmm7[2]
            macro eq32 tz_next = xmm5 {xmm0}

            jmp _next_dx3

            _greater3:
            mov dword [iz_step], 1
            macro broadcast xmm4 = xmm2[2]
            macro eq32 iz_stop = xmm4 {xmm0}
            macro broadcast xmm5 = xmm6[2]
            macro eq32 tz_next = xmm5 {xmm0}
            jmp _next_dx3

            _equal3:
            mov ebp, dword [khuge]
            mov dword [iz_step], -1
            mov dword [iz_stop], -1
            mov dword [tz_next], ebp 

            _next_dx3:

            _traverse:

            ;cell = self.cells[ix + self.nx * iy + self.nx * self.ny * iz]
            mov eax, dword [n] ;self.nx
            mov ebx, dword [n+4] ;self.ny
            imul ebx, dword [ixyz+8]
            imul ebx, eax
            imul eax, dword [ixyz+4]
            add eax, ebx
            add eax, dword [ixyz] ; in eax we have index
            imul eax, eax, 4 ; offset in bytes

            ;if tx_next < ty_next and tx_next < tz_next:
            macro eq32 xmm0 = tx_next
            macro if xmm0 > ty_next goto _next_part
            macro if xmm0 > tz_next goto _next_part

            mov ebp, dword [grid_ptr]
            add ebp, eax ;address + offset in bytes
            mov eax, dword [ebp]
            cmp eax, 0 ;empty cell
            je _next_calc

            ;eax - ray  ,ebx = hp, edx - ptr array 
            mov edx, dword [arr_ptr]
            add edx, eax
            mov eax, dword [ray_ptr]
        """
        code += "call " + label_ray_shapes + "\n" + """
            ;if hp and hp.t < tx_next: return hp
            cmp eax, 0
            je _next_calc
            macro if xmm0 < tx_next goto _return_hp

            _next_calc:
            macro eq32 xmm0 = dtxyz + tx_next
            macro eq32 tx_next = xmm0 {xmm7}
            mov eax, dword [ix_step]
            mov ebx, dword [ix_stop]
            mov ecx, dword [ixyz]
            add ecx, eax
            mov dword [ixyz], ecx
            cmp ecx, ebx
            jne _traverse
            mov eax, 0
            ret

            _next_part:
            ;if ty_next < tz_next:
            macro eq32 xmm0 = ty_next
            macro if xmm0 > tz_next goto _next_part2

            mov ebp, dword [grid_ptr]
            add ebp, eax ;address + offset in bytes
            mov eax, dword [ebp]
            cmp eax, 0 ;empty cell
            je _next_calc2

            ;eax - ray  ,ebx = hp, edx - ptr array 
            mov edx, dword [arr_ptr]
            add edx, eax
            mov eax, dword [ray_ptr]
        """
        code += "call " + label_ray_shapes + "\n" + """
            ;if hp and hp.t < ty_next: return hp
            cmp eax, 0
            je _next_calc2
            macro if xmm0 < ty_next goto _return_hp

            _next_calc2:
            macro eq128 xmm0 = dtxyz
            macro broadcast xmm0 = xmm0[1]
            macro eq32 xmm0 = xmm0 + ty_next
            macro eq32 ty_next = xmm0 {xmm7}
            mov eax, dword [iy_step]
            mov ebx, dword [iy_stop]
            mov ecx, dword [ixyz+4]
            add ecx, eax
            mov dword [ixyz+4], ecx
            cmp ecx, ebx
            jne _traverse
            mov eax, 0
            ret

            _next_part2:
            mov ebp, dword [grid_ptr]
            add ebp, eax ;address + offset in bytes
            mov eax, dword [ebp]
            cmp eax, 0 ;empty cell
            je _next_calc3

            ;eax - ray  ,ebx = hp, edx - ptr array 
            mov edx, dword [arr_ptr]
            add edx, eax
            mov eax, dword [ray_ptr]
        """
        code += "call " + label_ray_shapes + "\n" + """
            ;if hp and hp.t < tz_next: return hp
            cmp eax, 0
            je _next_calc3
            macro if xmm0 < tz_next goto _return_hp

            _next_calc3:
            macro eq128 xmm0 = dtxyz
            macro broadcast xmm0 = xmm0[2]
            macro eq32 xmm0 = xmm0 + tz_next
            macro eq32 tz_next = xmm0 {xmm7}
            mov eax, dword [iz_step]
            mov ebx, dword [iz_stop]
            mov ecx, dword [ixyz+8]
            add ecx, eax
            mov dword [ixyz+8], ecx
            cmp ecx, ebx
            jne _traverse
            mov eax, 0
            ret

            _return_hp:
            mov eax, 1
            ret

            _end_isect:
            mov eax, 0
            ret 
            

        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_scene_isect" + str(abs(hash(self)))
        for r in runtimes:
            if not r.global_exists(label):
                ds = r.load(name, mc)
                bbox = self.bbox
                ds["grid_ptr"] = self.asm_cells_b.ptr()
                ds['arr_ptr'] = self.lin_arrays_b[r].ptr() 
                ds["bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0) 
                ds["bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)
                nboxx = float(self.nx / (bbox.x1 - bbox.x0))
                nboxy = float(self.ny / (bbox.y1 - bbox.y0))
                nboxz = float(self.nz / (bbox.z1 - bbox.z0))
                ds["nbox_width"] = (nboxx, nboxy, nboxz, 0.0)
                ds["n_1"] = (float(self.nx-1), float(self.ny-1), float(self.nz-1), 0.0)
                ds["one_overn"] = (1.0 / self.nx, 1.0 / self.ny, 1.0 / self.nz, 0.0)
                ds["grid_size"] = (self.nx, self.ny, self.nz, 0)

    # eax - pointer to ray
    # ebx - pointer to hitpoint
    def isect_asm(self, runtimes, label, assembler, structures, dyn_arrays, intersector):
        self._load_isect_functions(runtimes, assembler, structures, dyn_arrays)
        self._create_grid(runtimes, intersector)
        label_ray_shapes = "ray_objects_intersections"
        self.isect_ray_shapes(runtimes, label_ray_shapes, assembler, structures)

        code = """
            #DATA
        """
        code += structures.structs(('ray', 'hitpoint')) + """
        uint32 hp_ptr, ray_ptr
        float one[4] = 1.0, 1.0, 1.0, 0.0
        float zero[4] = 0.0, 0.0, 0.0, 0.0
        uint32 ones = 0xFFFFFFFF
        int32 ixyz[4]
        float dtxyz[4]
        int32 ix_step, iy_step, iz_step
        int32 ix_stop, iy_stop, iz_stop
        float tx_next, ty_next, tz_next
        float khuge = 999999.999
        float minimum_distance = 999999.0
        int32 n[4]

        uint32 grid_ptr
        uint32 arr_ptr
        float bbox_min[4]
        float bbox_max[4]
        float nbox_width[4]
        float n_1[4]
        float one_overn[4]
        uint32 grid_size[4]
        
        #CODE
        """
        code += " global " + label + ":\n" + """
            mov dword [hp_ptr], ebx 
            mov dword [ray_ptr], eax
            mov ebp, dword [khuge]
            mov dword [minimum_distance], ebp
        """
        #TODO --- think if ray direction has zero component -- put some epsilon!!!
        code += """
            macro eq128 xmm0 = one / eax.ray.dir
        """
        code += "macro eq128 xmm1 = bbox_min\n"
        code += "macro eq128 xmm2 = bbox_max\n"
        code += """

            macro eq128 xmm1 = xmm1 - eax.ray.origin
            macro eq128 xmm1 = xmm1 * xmm0

            macro eq128 xmm2 = xmm2 - eax.ray.origin
            macro eq128 xmm2 = xmm2 * xmm0

            macro eq128 xmm3 = xmm1
            macro eq128 xmm4 = xmm2

            ; tx_min, ty_min, tz_min
            macro call minps xmm3, xmm2
            ; tx_max, ty_max, tz_max
            macro call maxps xmm4, xmm1

            macro broadcast xmm5 = xmm3[1]
            macro call maxss xmm5, xmm3
            macro broadcast xmm6 = xmm3[2]
            ;t0
            macro call maxss xmm6, xmm5

            macro broadcast xmm5 = xmm4[1]
            macro call minss xmm5, xmm4
            macro broadcast xmm7 = xmm4[2]
            ;t1
            macro call minss xmm7, xmm5
            
            macro if xmm7 > xmm6 goto next_section
            mov eax, 0 ;no intersection ocur
            ret
            
            ;now we must check this if self.bbox.inside(ray.origin) 
            next_section:
            macro eq128 xmm0 = eax.ray.origin
            macro eq128 xmm2 = xmm0
        """
        code += "macro eq128 xmm1 = bbox_max\n"
        code += """
            ; le - less or equal (xmm0 <= xmm1)
            macro call cmpps xmm0, xmm1, 2
        """
        code += "macro eq128 xmm5 = bbox_min\n"
        code += """
            macro call cmpps xmm5, xmm2, 2 
            macro call andps xmm0, xmm5
            macro broadcast xmm1 = xmm0[1]
            macro broadcast xmm2 = xmm0[2]
            macro call andps xmm0, xmm1
            macro call andps xmm0, xmm2
        """
        if proc.AVX:
            code += "vcomiss xmm0, dword [ones] \n"
        else:
            code += "comiss xmm0, dword [ones] \n"

        code += """
            jz point_inside ; point is inside bbox

            macro eq128 xmm0 = eax.ray.dir * xmm6 + eax.ray.origin
            jmp next_section2

            point_inside:
            macro eq128 xmm0 = eax.ray.origin

            next_section2:
        """
        code +=  "macro eq128 xmm0 = xmm0 - bbox_min\n"
        code +=  "macro eq128 xmm0 = xmm0 * nbox_width\n"
        code +=  "macro eq128 xmm2 = n_1\n"
        code += """
            macro call zero xmm1
            macro call minps xmm0, xmm2
            macro call maxps xmm0, xmm1
            ; ix, iy, iz
        """
        if proc.AVX:
            code += """
            vcvttps2dq xmm1, xmm0
            vcvtdq2ps xmm0, xmm1
            """
        else:
            code += """
            cvttps2dq xmm1, xmm0
            cvtdq2ps xmm0, xmm1
            """
        code += """
            macro eq128 ixyz = xmm1 {xmm7}
            macro eq128 xmm5 = xmm4
            macro eq128 xmm5 = xmm5 - xmm3
        """
        code += "macro eq128 xmm5 = xmm5 * one_overn\n"
        code += """
            ; xmm5 = dtx, dty, dtz
            macro eq128 dtxyz = xmm5 {xmm7}

            ;tx_next = tx_min + (ix + 1) * dtx
            ;tx_next = tx_min + (self.nx - ix) * dtx
            macro eq128 xmm6 = one
            macro eq128 xmm6 = xmm6 + xmm0
            macro eq128 xmm6 = xmm6 * xmm5
            macro eq128 xmm6 = xmm6 + xmm3
        """
        code += "macro eq128 xmm7 = grid_size\n"
        code += """
            macro eq128 n = xmm7 {xmm0}
            macro eq128 xmm2 = xmm7
            macro call int_to_float xmm7, xmm7
            macro eq128 xmm7 = xmm7 - xmm0
            macro eq128 xmm7 = xmm7 * xmm5
            macro eq128 xmm7 = xmm7 + xmm3

            macro eq128 xmm0 = eax.ray.dir
        """
        if proc.AVX:
            code += "vcomiss xmm0, dword [zero]\n" 
        else:
            code += "comiss xmm0, dword [zero]\n" 
        code += """
            jz _equal1
            jnc _greater1

            mov dword [ix_step], -1
            mov dword [ix_stop], -1
            macro eq32 tx_next = xmm7 {xmm0}

            jmp _next_dx

            _greater1:
            mov dword [ix_step], 1
            macro eq32 ix_stop = xmm2 {xmm0}
            macro eq32 tx_next = xmm6 {xmm0}
            jmp _next_dx

            _equal1:
            mov ebp, dword [khuge]
            mov dword [ix_step], -1
            mov dword [ix_stop], -1
            mov dword [tx_next], ebp 

            _next_dx:
            macro broadcast xmm1 = xmm0[1]
        """
        if proc.AVX:
            code += "vcomiss xmm1, dword [zero]\n" 
        else:
            code += "comiss xmm1, dword [zero]\n" 
        code += """
            jz _equal2
            jnc _greater2

            mov dword [iy_step], -1
            mov dword [iy_stop], -1
            macro broadcast xmm5 = xmm7[1]
            macro eq32 ty_next = xmm5 {xmm0}

            jmp _next_dx2

            _greater2:
            mov dword [iy_step], 1
            macro broadcast xmm4 = xmm2[1]
            macro eq32 iy_stop = xmm4 {xmm0}
            macro broadcast xmm5 = xmm6[1]
            macro eq32 ty_next = xmm5 {xmm0}
            jmp _next_dx2

            _equal2:
            mov ebp, dword [khuge]
            mov dword [iy_step], -1
            mov dword [iy_stop], -1
            mov dword [ty_next], ebp 

            _next_dx2:
            macro broadcast xmm1 = xmm0[2]
        """
        if proc.AVX:
            code += "vcomiss xmm1, dword [zero]\n" 
        else:
            code += "comiss xmm1, dword [zero]\n" 
        code += """
            jz _equal3
            jnc _greater3

            mov dword [iz_step], -1
            mov dword [iz_stop], -1
            macro broadcast xmm5 = xmm7[2]
            macro eq32 tz_next = xmm5 {xmm0}

            jmp _next_dx3

            _greater3:
            mov dword [iz_step], 1
            macro broadcast xmm4 = xmm2[2]
            macro eq32 iz_stop = xmm4 {xmm0}
            macro broadcast xmm5 = xmm6[2]
            macro eq32 tz_next = xmm5 {xmm0}
            jmp _next_dx3

            _equal3:
            mov ebp, dword [khuge]
            mov dword [iz_step], -1
            mov dword [iz_stop], -1
            mov dword [tz_next], ebp 

            _next_dx3:

            _traverse:

            ;cell = self.cells[ix + self.nx * iy + self.nx * self.ny * iz]
            mov eax, dword [n] ;self.nx
            mov ebx, dword [n+4] ;self.ny
            imul ebx, dword [ixyz+8]
            imul ebx, eax
            imul eax, dword [ixyz+4]
            add eax, ebx
            add eax, dword [ixyz] ; in eax we have index
            imul eax, eax, 4 ; offset in bytes

            ;if tx_next < ty_next and tx_next < tz_next:
            macro eq32 xmm0 = tx_next
            macro if xmm0 > ty_next goto _next_part
            macro if xmm0 > tz_next goto _next_part

            mov ebp, dword [grid_ptr]
            add ebp, eax ;address + offset in bytes
            mov eax, dword [ebp]
            cmp eax, 0 ;empty cell
            je _next_calc

            ;eax - ray  ,ebx = hp, edx - ptr array 
            mov edx, dword [arr_ptr]
            add edx, eax
            mov eax, dword [ray_ptr]
            mov ebx, dword [hp_ptr]
        """
        code += "call " + label_ray_shapes + "\n" + """
            ;if hp and hp.t < tx_next: return hp
            cmp eax, 0
            je _next_calc
            mov ebx, dword [hp_ptr]
            macro eq32 xmm0 = ebx.hitpoint.t
            macro if xmm0 < tx_next goto _return_hp

            _next_calc:
            macro eq32 xmm0 = dtxyz + tx_next
            macro eq32 tx_next = xmm0 {xmm7}
            mov eax, dword [ix_step]
            mov ebx, dword [ix_stop]
            mov ecx, dword [ixyz]
            add ecx, eax
            mov dword [ixyz], ecx
            cmp ecx, ebx
            jne _traverse
            mov eax, 0
            ret

            _next_part:
            ;if ty_next < tz_next:
            macro eq32 xmm0 = ty_next
            macro if xmm0 > tz_next goto _next_part2

            mov ebp, dword [grid_ptr]
            add ebp, eax ;address + offset in bytes
            mov eax, dword [ebp]
            cmp eax, 0 ;empty cell
            je _next_calc2

            ;eax - ray  ,ebx = hp, edx - ptr array 
            mov edx, dword [arr_ptr]
            add edx, eax
            mov eax, dword [ray_ptr]
            mov ebx, dword [hp_ptr]
        """
        code += "call " + label_ray_shapes + "\n" + """
            ;if hp and hp.t < ty_next: return hp
            cmp eax, 0
            je _next_calc2
            mov ebx, dword [hp_ptr]
            macro eq32 xmm0 = ebx.hitpoint.t
            macro if xmm0 < ty_next goto _return_hp

            _next_calc2:
            macro eq128 xmm0 = dtxyz
            macro broadcast xmm0 = xmm0[1]
            macro eq32 xmm0 = xmm0 + ty_next
            macro eq32 ty_next = xmm0 {xmm7}
            mov eax, dword [iy_step]
            mov ebx, dword [iy_stop]
            mov ecx, dword [ixyz+4]
            add ecx, eax
            mov dword [ixyz+4], ecx
            cmp ecx, ebx
            jne _traverse
            mov eax, 0
            ret

            _next_part2:
            mov ebp, dword [grid_ptr]
            add ebp, eax ;address + offset in bytes
            mov eax, dword [ebp]
            cmp eax, 0 ;empty cell
            je _next_calc3

            ;eax - ray  ,ebx = hp, edx - ptr array 
            mov edx, dword [arr_ptr]
            add edx, eax
            mov eax, dword [ray_ptr]
            mov ebx, dword [hp_ptr]
        """
        code += "call " + label_ray_shapes + "\n" + """
            ;if hp and hp.t < tz_next: return hp
            cmp eax, 0
            je _next_calc3
            mov ebx, dword [hp_ptr]
            macro eq32 xmm0 = ebx.hitpoint.t
            macro if xmm0 < tz_next goto _return_hp

            _next_calc3:
            macro eq128 xmm0 = dtxyz
            macro broadcast xmm0 = xmm0[2]
            macro eq32 xmm0 = xmm0 + tz_next
            macro eq32 tz_next = xmm0 {xmm7}
            mov eax, dword [iz_step]
            mov ebx, dword [iz_stop]
            mov ecx, dword [ixyz+8]
            add ecx, eax
            mov dword [ixyz+8], ecx
            cmp ecx, ebx
            jne _traverse
            mov eax, 0
            ret

            _return_hp:
            mov eax, 1
            ret

            _end_isect:
            mov eax, 0
            ret 
            

        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_scene_isect" + str(abs(hash(self)))
        for r in runtimes:
            if not r.global_exists(label):
                ds = r.load(name, mc)
                bbox = self.bbox
                ds["grid_ptr"] = self.asm_cells.ptr()
                ds['arr_ptr'] = self.lin_arrays[r].ptr() 
                ds["bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0) 
                ds["bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)
                nboxx = float(self.nx / (bbox.x1 - bbox.x0))
                nboxy = float(self.ny / (bbox.y1 - bbox.y0))
                nboxz = float(self.nz / (bbox.z1 - bbox.z0))
                ds["nbox_width"] = (nboxx, nboxy, nboxz, 0.0)
                ds["n_1"] = (float(self.nx-1), float(self.ny-1), float(self.nz-1), 0.0)
                ds["one_overn"] = (1.0 / self.nx, 1.0 / self.ny, 1.0 / self.nz, 0.0)
                ds["grid_size"] = (self.nx, self.ny, self.nz, 0)


    # eax = pointer to ray structure
    # ebx = pointer to hitpoint structure
    # edx = address in linear grid array --- n:{obj,func}, {obj,func}, ... 
    def isect_ray_shapes(self, runtimes, label, assembler, structures):

        code = """
            #DATA
        """
        code += structures.structs(('ray', 'hitpoint')) + """

        uint32 isect_ocur 
        float min_dist = 999999.0
        float max_dist = 999999.0
        uint32 ptr_ray
        uint32 ptr_hp
        uint32 nobjects
        uint32 ptr_objfuncs
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov dword [ptr_ray], eax
        mov dword [ptr_hp], ebx

        mov esi, dword [edx]
        mov dword [nobjects], esi 
        add edx, 4
        mov dword [ptr_objfuncs], edx
        mov dword [isect_ocur], 0
        mov edi, dword [max_dist]
        mov dword [min_dist], edi

        _objects_loop:
        mov eax, dword [ptr_ray]
        mov esi, dword [ptr_objfuncs]
        mov ebx, dword [esi]

        mov ecx, min_dist
        mov edx, dword [ptr_hp]
        call dword [esi + 4]  ; function pointer


        cmp eax, 0
        je _next_object 
        mov dword [isect_ocur], 1
        ; update distance
        mov eax, dword [ptr_hp]
        mov ebx, dword [eax + hitpoint.t]
        mov dword [min_dist], ebx

        
        _next_object:
        add dword [ptr_objfuncs], 8
        sub dword [nobjects], 1  
        jnz _objects_loop

        mov eax, dword [isect_ocur]
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_objcest_isects" + str(abs(hash(self)))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    # eax = pointer to ray structure
    # edx = address in linear grid array --- n:{obj,func}, {obj,func}, ... 
    def isect_ray_shapes_b(self, runtimes, label, assembler, structures):

        code = """
            #DATA
        """
        code += structures.structs(('ray', 'hitpoint')) + """

        uint32 isect_ocur 
        float min_dist = 999999.0
        float max_dist = 999999.0
        uint32 ptr_ray
        uint32 nobjects
        uint32 ptr_objfuncs
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov dword [ptr_ray], eax

        mov esi, dword [edx]
        mov dword [nobjects], esi 
        add edx, 4
        mov dword [ptr_objfuncs], edx
        mov dword [isect_ocur], 0
        mov edi, dword [max_dist]
        mov dword [min_dist], edi

        _objects_loop:
        mov eax, dword [ptr_ray]
        mov esi, dword [ptr_objfuncs]
        mov ebx, dword [esi]

        mov ecx, min_dist
        call dword [esi + 4]  ; function pointer

        cmp eax, 0
        je _next_object 
        mov dword [isect_ocur], 1
        ; update distance
        macro eq32 min_dist = xmm0 {xmm7}

        
        _next_object:
        add dword [ptr_objfuncs], 8
        sub dword [nobjects], 1  
        jnz _objects_loop

        mov eax, dword [isect_ocur]
        macro eq32 xmm0 = min_dist
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_objcest_isects" + str(abs(hash(self)))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)


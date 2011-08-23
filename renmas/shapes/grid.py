
from tdasm import Tdasm, Runtime
import renmas
import renmas.core
import renmas.utils as util
from renmas.shapes import BBox
from renmas.maths import Vector3
import math
import x86

from .funcs import multiple_isect_asm

SSE_ASM = """
        mov dword [hp_ptr], edx
        mov dword [ray_ptr], eax
        mov dword [grid_ptr], ebx

        macro eq128 xmm0 = one
        macro eq128 xmm0 = xmm0 / eax.ray.dir

        macro eq128 xmm1 = ebx.grid.bbox_min
        macro eq128 xmm2 = ebx.grid.bbox_max

        macro eq128 xmm1 = xmm1 - eax.ray.origin {xmm0, xmm2}
        macro eq128 xmm1 = xmm1 * xmm0 {xmm2}

        macro eq128 xmm2 = xmm2 - eax.ray.origin {xmm0, xmm1}
        macro eq128 xmm2 = xmm2 * xmm0 {xmm1}

        
        macro eq128 xmm3 = xmm1
        macro eq128 xmm4 = xmm2
       
        minps xmm3, xmm2 ; tx_min, ty_min, tz_min
        maxps xmm4, xmm1 ; tx_max, ty_max, tz_max

        macro broadcast xmm5 = xmm3[1]
        maxss xmm5, xmm3
        macro broadcast xmm6 = xmm3[2]
        maxss xmm6, xmm5 ;t0

        macro broadcast xmm5 = xmm4[1]
        minss xmm5, xmm4
        macro broadcast xmm7 = xmm4[2]
        minss xmm7, xmm5 ;t1 
        
        macro if xmm7 > xmm6 goto next_section
        mov eax, 0 ;no intersection ocur
        ret

        next_section:
        ;now we must check this if self.bbox.inside(ray.origin) 
        macro eq128 xmm0 = eax.ray.origin
        macro eq128 xmm2 = xmm0
        macro eq128 xmm1 = ebx.grid.bbox_max
        cmpps xmm0, xmm1, 2 ; le - less or equal (xmm0 <= xmm1)
        macro eq128 xmm5 = ebx.grid.bbox_min
        cmpps xmm5, xmm2, 2 
        andps xmm0, xmm5
        macro broadcast xmm1 = xmm0[1]
        macro broadcast xmm2 = xmm0[2]
        andps xmm0, xmm1
        andps xmm0, xmm2
        comiss xmm0, dword [ones]

        jz point_inside ; point is inside bbox
        macro eq128 xmm0 = eax.ray.dir
        macro eq128 xmm0 = xmm0 * xmm6
        macro eq128 xmm0 = xmm0 + eax.ray.origin
        jmp next_section2

        point_inside:
        macro eq128 xmm0 = eax.ray.origin

        next_section2:
        macro eq128 xmm0 = xmm0 - ebx.grid.bbox_min
        macro eq128 xmm0 = xmm0 * ebx.grid.nbox_width
        macro eq128 xmm2 = ebx.grid.n_1 
        macro eq128 xmm1 = zero
        minps xmm0, xmm2
        maxps xmm0, xmm1
        cvttps2dq xmm1, xmm0  ; ix, iy, iz
        cvtdq2ps xmm0, xmm1
        movaps oword [ixyz], xmm1

        macro eq128 xmm5 = xmm4
        macro eq128 xmm5 = xmm5 - xmm3
        macro eq128 xmm5 = xmm5 * ebx.grid.one_overn 
        ; xmm5 = dtx, dty, dtz
        movaps oword [dtxyz], xmm5

        ;tx_next = tx_min + (ix + 1) * dtx
        ;tx_next = tx_min + (self.nx - ix) * dtx
        macro eq128 xmm6 = one
        macro eq128 xmm6 = xmm6 + xmm0
        macro eq128 xmm6 = xmm6 * xmm5
        macro eq128 xmm6 = xmm6 + xmm3

        macro eq128 xmm7 = ebx.grid.n
        movaps oword [n], xmm7
        macro eq128 xmm2 = xmm7
        cvtdq2ps xmm7, xmm7
        macro eq128 xmm7 = xmm7 - xmm0
        macro eq128 xmm7 = xmm7 * xmm5
        macro eq128 xmm7 = xmm7 + xmm3
        
        macro eq128 xmm0 = eax.ray.dir
        comiss xmm0, dword [zero] 
        jz _equal1
        jnc _greater1

        mov dword [istep], -1
        mov dword [istop], -1
        movss dword [tnext], xmm7

        jmp _next_dx

        _greater1:
        mov dword [istep], 1
        movss dword [istop], xmm2
        movss dword [tnext], xmm6
        jmp _next_dx

        _equal1:
        mov ebp, dword [khuge]
        mov dword [istep], -1
        mov dword [istop], -1
        mov dword [tnext], ebp 

        _next_dx:
        macro broadcast xmm1 = xmm0[1]
        comiss xmm1, dword [zero] 
        jz _equal2
        jnc _greater2

        mov dword [istep+4], -1
        mov dword [istop+4], -1
        macro broadcast xmm5 = xmm7[1]
        movss dword [tnext+4], xmm5

        jmp _next_dx2

        _greater2:
        mov dword [istep+4], 1
        macro broadcast xmm4 = xmm2[1]
        movss dword [istop+4], xmm4
        macro broadcast xmm5 = xmm6[1]
        movss dword [tnext+4], xmm5
        jmp _next_dx2

        _equal2:
        mov ebp, dword [khuge]
        mov dword [istep+4], -1
        mov dword [istop+4], -1
        mov dword [tnext+4], ebp 

        _next_dx2:
        macro broadcast xmm1 = xmm0[2]
        comiss xmm1, dword [zero] 
        jz _equal3
        jnc _greater3

        mov dword [istep+8], -1
        mov dword [istop+8], -1
        macro broadcast xmm5 = xmm7[2]
        movss dword [tnext+8], xmm5

        jmp _next_dx3

        _greater3:
        mov dword [istep+8], 1
        macro broadcast xmm4 = xmm2[2]
        movss dword [istop+8], xmm4
        macro broadcast xmm5 = xmm6[2]
        movss dword [tnext+8], xmm5
        jmp _next_dx3

        _equal3:
        mov ebp, dword [khuge]
        mov dword [istep+8], -1
        mov dword [istop+8], -1
        mov dword [tnext+8], ebp 

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
        movss xmm0, dword [tnext] ;tx_next
        comiss xmm0, dword [tnext+4]
        jnc _next_part
        comiss xmm0, dword [tnext+8]
        jnc _next_part

        mov edx, dword [grid_ptr]
        mov ebp, dword [edx + grid.grid_ptr]
        add ebp, eax ;address + offset in bytes
        mov eax, dword [ebp]
        cmp eax, 0 ;empty cell
        je _next_calc
        ;now we must call multiple object hit function
        mov ecx, dword [edx + grid.arr_ptr]
        add ecx, eax ; arr n:obj,func

        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        mov eax, dword [ray_ptr]
        mov ebx, dword [hp_ptr]
        mov edi, dword [ecx]
        add ecx, 4
        mov esi, ecx
        call multiple_isect 
        cmp eax, 0
        je _next_calc
        mov eax, dword [hp_ptr]
        movss xmm0, dword [eax + hitpoint.t]
        comiss xmm0, dword [tnext]
        jnc _next_calc
        mov eax, 1 
        ret
        
        _next_calc:
        movss xmm0, dword [dtxyz] 
        addss xmm0, dword [tnext]
        movss dword [tnext], xmm0
        mov eax, dword [istep]
        mov ebx, dword [istop]
        mov ecx, dword [ixyz]
        add ecx, eax
        mov dword [ixyz], ecx
        cmp ecx, ebx
        jne _traverse
        mov eax, 0
        ret

        _next_part:
        ;if ty_next < tz_next:
        movss xmm0, dword [tnext + 4]
        comiss xmm0, dword [tnext + 8]
        jnc _next_part2

        mov edx, dword [grid_ptr]
        mov ebp, dword [edx + grid.grid_ptr]
        add ebp, eax ;address + offset in bytes
        mov eax, dword [ebp]
        cmp eax, 0 ;empty cell
        je _next_calc2
        ;now we must call multiple object hit function
        mov ecx, dword [edx + grid.arr_ptr]
        add ecx, eax ; arr n:obj,func

        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        mov eax, dword [ray_ptr]
        mov ebx, dword [hp_ptr]
        mov edi, dword [ecx]
        add ecx, 4
        mov esi, ecx
        call multiple_isect 
        cmp eax, 0
        je _next_calc2
        mov eax, dword [hp_ptr]
        movss xmm0, dword [eax + hitpoint.t]
        comiss xmm0, dword [tnext+4]
        jnc _next_calc2
        mov eax, 1
        ret

        _next_calc2:
        movss xmm0, dword [dtxyz+4]
        addss xmm0, dword [tnext+4]
        movss dword [tnext+4], xmm0
        mov eax, dword [istep+4]
        mov ebx, dword [istop+4]
        mov ecx, dword [ixyz+4]
        add ecx, eax
        mov dword [ixyz+4], ecx
        cmp ecx, ebx
        jne _traverse
        mov eax, 0
        ret

        _next_part2:

        mov edx, dword [grid_ptr]
        mov ebp, dword [edx + grid.grid_ptr]
        add ebp, eax ;address + offset in bytes
        mov eax, dword [ebp]
        cmp eax, 0 ;empty cell
        je _next_calc3
        ;now we must call multiple object hit function
        mov ecx, dword [edx + grid.arr_ptr]
        add ecx, eax ; arr n:obj,func

        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        mov eax, dword [ray_ptr]
        mov ebx, dword [hp_ptr]
        mov edi, dword [ecx]
        add ecx, 4
        mov esi, ecx
        call multiple_isect 
        cmp eax, 0
        je _next_calc3
        mov eax, dword [hp_ptr]
        movss xmm0, dword [eax + hitpoint.t]
        comiss xmm0, dword [tnext+8]
        jnc _next_calc3
        mov eax, 1
        ret

        _next_calc3:
        movss xmm0, dword [dtxyz+8]
        addss xmm0, dword [tnext+8]
        movss dword [tnext+8], xmm0
        mov eax, dword [istep+8]
        mov ebx, dword [istop+8]
        mov ecx, dword [ixyz+8]
        add ecx, eax
        mov dword [ixyz+8], ecx
        cmp ecx, ebx
        jne _traverse
        mov eax, 0
        ret


        """

AVX_ASM = """
        mov dword [hp_ptr], edx
        mov dword [ray_ptr], eax
        mov dword [grid_ptr], ebx

        macro eq128 xmm0 = one
        macro eq128 xmm0 = xmm0 / eax.ray.dir

        macro eq128 xmm1 = ebx.grid.bbox_min
        macro eq128 xmm2 = ebx.grid.bbox_max

        macro eq128 xmm1 = xmm1 - eax.ray.origin {xmm0, xmm2}
        macro eq128 xmm1 = xmm1 * xmm0 {xmm2}

        macro eq128 xmm2 = xmm2 - eax.ray.origin {xmm0, xmm1}
        macro eq128 xmm2 = xmm2 * xmm0 {xmm1}

        
        macro eq128 xmm3 = xmm1
        macro eq128 xmm4 = xmm2
       
        vminps xmm3, xmm3, xmm2 ; tx_min, ty_min, tz_min
        vmaxps xmm4, xmm4, xmm1 ; tx_max, ty_max, tz_max

        macro broadcast xmm5 = xmm3[1]
        vmaxss xmm5, xmm5, xmm3
        macro broadcast xmm6 = xmm3[2]
        vmaxss xmm6, xmm6, xmm5 ;t0

        macro broadcast xmm5 = xmm4[1]
        vminss xmm5, xmm5, xmm4
        macro broadcast xmm7 = xmm4[2]
        vminss xmm7, xmm7, xmm5 ;t1 
        
        macro if xmm7 > xmm6 goto next_section
        mov eax, 0 ;no intersection ocur
        ret

        next_section:
        ;now we must check this if self.bbox.inside(ray.origin) 
        macro eq128 xmm0 = eax.ray.origin
        macro eq128 xmm2 = xmm0
        macro eq128 xmm1 = ebx.grid.bbox_max
        vcmpps xmm0, xmm0, xmm1, 2 ; le - less or equal (xmm0 <= xmm1)
        macro eq128 xmm5 = ebx.grid.bbox_min
        vcmpps xmm5, xmm5, xmm2, 2 
        vandps xmm0, xmm0, xmm5
        macro broadcast xmm1 = xmm0[1]
        macro broadcast xmm2 = xmm0[2]
        vandps xmm0, xmm0, xmm1
        vandps xmm0, xmm0, xmm2
        vcomiss xmm0, dword [ones]

        jz point_inside ; point is inside bbox
        macro eq128 xmm0 = eax.ray.dir
        macro eq128 xmm0 = xmm0 * xmm6
        macro eq128 xmm0 = xmm0 + eax.ray.origin
        jmp next_section2

        point_inside:
        macro eq128 xmm0 = eax.ray.origin

        next_section2:
        macro eq128 xmm0 = xmm0 - ebx.grid.bbox_min
        macro eq128 xmm0 = xmm0 * ebx.grid.nbox_width
        macro eq128 xmm2 = ebx.grid.n_1 
        macro eq128 xmm1 = zero
        vminps xmm0, xmm0, xmm2
        vmaxps xmm0, xmm0, xmm1
        vcvttps2dq xmm1, xmm0  ; ix, iy, iz
        vcvtdq2ps xmm0, xmm1
        vmovaps oword [ixyz], xmm1

        macro eq128 xmm5 = xmm4
        macro eq128 xmm5 = xmm5 - xmm3
        macro eq128 xmm5 = xmm5 * ebx.grid.one_overn 
        ; xmm5 = dtx, dty, dtz
        vmovaps oword [dtxyz], xmm5

        ;tx_next = tx_min + (ix + 1) * dtx
        ;tx_next = tx_min + (self.nx - ix) * dtx
        macro eq128 xmm6 = one
        macro eq128 xmm6 = xmm6 + xmm0
        macro eq128 xmm6 = xmm6 * xmm5
        macro eq128 xmm6 = xmm6 + xmm3

        macro eq128 xmm7 = ebx.grid.n
        vmovaps oword [n], xmm7
        macro eq128 xmm2 = xmm7
        vcvtdq2ps xmm7, xmm7
        macro eq128 xmm7 = xmm7 - xmm0
        macro eq128 xmm7 = xmm7 * xmm5
        macro eq128 xmm7 = xmm7 + xmm3
        
        macro eq128 xmm0 = eax.ray.dir
        vcomiss xmm0, dword [zero] 
        jz _equal1
        jnc _greater1

        mov dword [istep], -1
        mov dword [istop], -1
        vmovss dword [tnext], xmm7

        jmp _next_dx

        _greater1:
        mov dword [istep], 1
        vmovss dword [istop], xmm2
        vmovss dword [tnext], xmm6
        jmp _next_dx

        _equal1:
        mov ebp, dword [khuge]
        mov dword [istep], -1
        mov dword [istop], -1
        mov dword [tnext], ebp 

        _next_dx:
        macro broadcast xmm1 = xmm0[1]
        vcomiss xmm1, dword [zero] 
        jz _equal2
        jnc _greater2

        mov dword [istep+4], -1
        mov dword [istop+4], -1
        macro broadcast xmm5 = xmm7[1]
        vmovss dword [tnext+4], xmm5

        jmp _next_dx2

        _greater2:
        mov dword [istep+4], 1
        macro broadcast xmm4 = xmm2[1]
        vmovss dword [istop+4], xmm4
        macro broadcast xmm5 = xmm6[1]
        vmovss dword [tnext+4], xmm5
        jmp _next_dx2

        _equal2:
        mov ebp, dword [khuge]
        mov dword [istep+4], -1
        mov dword [istop+4], -1
        mov dword [tnext+4], ebp 

        _next_dx2:
        macro broadcast xmm1 = xmm0[2]
        vcomiss xmm1, dword [zero] 
        jz _equal3
        jnc _greater3

        mov dword [istep+8], -1
        mov dword [istop+8], -1
        macro broadcast xmm5 = xmm7[2]
        vmovss dword [tnext+8], xmm5

        jmp _next_dx3

        _greater3:
        mov dword [istep+8], 1
        macro broadcast xmm4 = xmm2[2]
        vmovss dword [istop+8], xmm4
        macro broadcast xmm5 = xmm6[2]
        vmovss dword [tnext+8], xmm5
        jmp _next_dx3

        _equal3:
        mov ebp, dword [khuge]
        mov dword [istep+8], -1
        mov dword [istop+8], -1
        mov dword [tnext+8], ebp 

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
        vmovss xmm0, dword [tnext] ;tx_next
        vcomiss xmm0, dword [tnext+4]
        jnc _next_part
        vcomiss xmm0, dword [tnext+8]
        jnc _next_part

        mov edx, dword [grid_ptr]
        mov ebp, dword [edx + grid.grid_ptr]
        add ebp, eax ;address + offset in bytes
        mov eax, dword [ebp]
        cmp eax, 0 ;empty cell
        je _next_calc
        ;now we must call multiple object hit function
        mov ecx, dword [edx + grid.arr_ptr]
        add ecx, eax ; arr n:obj,func

        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        mov eax, dword [ray_ptr]
        mov ebx, dword [hp_ptr]
        mov edi, dword [ecx]
        add ecx, 4
        mov esi, ecx
        call multiple_isect 
        cmp eax, 0
        je _next_calc
        mov eax, dword [hp_ptr]
        vmovss xmm0, dword [eax + hitpoint.t]
        vcomiss xmm0, dword [tnext]
        jnc _next_calc
        mov eax, 1 
        ret
        
        _next_calc:
        vmovss xmm0, dword [dtxyz] 
        vaddss xmm0, xmm0, dword [tnext]
        vmovss dword [tnext], xmm0
        mov eax, dword [istep]
        mov ebx, dword [istop]
        mov ecx, dword [ixyz]
        add ecx, eax
        mov dword [ixyz], ecx
        cmp ecx, ebx
        jne _traverse
        mov eax, 0
        ret

        _next_part:
        ;if ty_next < tz_next:
        vmovss xmm0, dword [tnext + 4]
        vcomiss xmm0, dword [tnext + 8]
        jnc _next_part2

        mov edx, dword [grid_ptr]
        mov ebp, dword [edx + grid.grid_ptr]
        add ebp, eax ;address + offset in bytes
        mov eax, dword [ebp]
        cmp eax, 0 ;empty cell
        je _next_calc2
        ;now we must call multiple object hit function
        mov ecx, dword [edx + grid.arr_ptr]
        add ecx, eax ; arr n:obj,func

        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        mov eax, dword [ray_ptr]
        mov ebx, dword [hp_ptr]
        mov edi, dword [ecx]
        add ecx, 4
        mov esi, ecx
        call multiple_isect 
        cmp eax, 0
        je _next_calc2
        mov eax, dword [hp_ptr]
        vmovss xmm0, dword [eax + hitpoint.t]
        vcomiss xmm0, dword [tnext+4]
        jnc _next_calc2
        mov eax, 1
        ret

        _next_calc2:
        vmovss xmm0, dword [dtxyz+4]
        vaddss xmm0, xmm0, dword [tnext+4]
        vmovss dword [tnext+4], xmm0
        mov eax, dword [istep+4]
        mov ebx, dword [istop+4]
        mov ecx, dword [ixyz+4]
        add ecx, eax
        mov dword [ixyz+4], ecx
        cmp ecx, ebx
        jne _traverse
        mov eax, 0
        ret

        _next_part2:

        mov edx, dword [grid_ptr]
        mov ebp, dword [edx + grid.grid_ptr]
        add ebp, eax ;address + offset in bytes
        mov eax, dword [ebp]
        cmp eax, 0 ;empty cell
        je _next_calc3
        ;now we must call multiple object hit function
        mov ecx, dword [edx + grid.arr_ptr]
        add ecx, eax ; arr n:obj,func

        ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
        mov eax, dword [ray_ptr]
        mov ebx, dword [hp_ptr]
        mov edi, dword [ecx]
        add ecx, 4
        mov esi, ecx
        call multiple_isect 
        cmp eax, 0
        je _next_calc3
        mov eax, dword [hp_ptr]
        vmovss xmm0, dword [eax + hitpoint.t]
        vcomiss xmm0, dword [tnext+8]
        jnc _next_calc3
        mov eax, 1
        ret

        _next_calc3:
        vmovss xmm0, dword [dtxyz+8]
        vaddss xmm0, xmm0, dword [tnext+8]
        vmovss dword [tnext+8], xmm0
        mov eax, dword [istep+8]
        mov ebx, dword [istop+8]
        mov ecx, dword [ixyz+8]
        add ecx, eax
        mov dword [ixyz+8], ecx
        cmp ecx, ebx
        jne _traverse
        mov eax, 0
        ret


        """


def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))

def isect(ray, shapes):
    min_dist = 999999.0
    hit_point = None
    for s in shapes:
        hit = s.isect(ray, min_dist)
        if hit is False: continue
        if hit.t < min_dist:
            min_dist = hit.t
            hit_point = hit
    return hit_point

class Grid:
    def __init__(self):
        self.bbox = None

    def setup(self, shapes):

        p0 = Vector3(9999999.0, 9999999.0, 9999999.0)
        p1 = Vector3(-9999999.0, -9999999.0, -9999999.0)
        bb_min = BBox(p0, p1, None) 

        for shape in shapes:
            bbox = shape.bbox()

            if bbox.x0 < bb_min.x0: bb_min.x0 = bbox.x0
            if bbox.y0 < bb_min.y0: bb_min.y0 = bbox.y0
            if bbox.z0 < bb_min.z0: bb_min.z0 = bbox.z0

            if bbox.x1 > bb_min.x1: bb_min.x1 = bbox.x1
            if bbox.y1 > bb_min.y1: bb_min.y1 = bbox.y1
            if bbox.z1 > bb_min.z1: bb_min.z1 = bbox.z1

        self.bbox = bb_min

        
        num_shapes = len(shapes) #FIXME when we incoorporate mesh
        wx = bb_min.x1 - bb_min.x0
        wy = bb_min.y1 - bb_min.y0
        wz = bb_min.z1 - bb_min.z0
        multiplier = 1.3 # about 8 times more cells than objects TODO test this!
        
        s = math.pow(wx * wy * wz / float(num_shapes), 0.333333)
        nx = int(multiplier * wx / s + 1)
        ny = int(multiplier * wy / s + 1)
        nz = int(multiplier * wz / s + 1)
        self.nx = nx
        self.ny = ny
        self.nz = nz

        num_cells = int(nx * ny * nz)
        print("wx=", wx, " wy=", wy, " wz=", wz)
        print("nx=", nx, " ny=", ny, " nz=", nz)

        # every cell have referencs to objects that are in that cell
        self.cells = [] # we need to initialize list
        for c in range(num_cells):
            self.cells.append([])

        max_len = 0
        num_arrays = 0
        num_objects = 0 

        for shape in shapes:
            bbox = shape.bbox()
    
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
                        num_objects += 1
                        if duzina == 1: num_arrays += 1
                        if duzina > max_len: max_len = duzina


        nx_1 = float(self.nx - 1) 
        ny_1 = float(self.ny - 1)
        nz_1 = float(self.nz - 1)
        self.n_1 = Vector3(nx_1, ny_1, nz_1)

        ovx = 1.0 / self.nx
        ovy = 1.0 / self.ny
        ovz = 1.0 / self.nz
        self.one_overn = Vector3(ovx, ovy, ovz)


        nboxx = float(self.nx / (self.bbox.x1 - self.bbox.x0))
        nboxy = float(self.ny / (self.bbox.y1 - self.bbox.y0))
        nboxz = float(self.nz / (self.bbox.z1 - self.bbox.z0))
        self.nbox_width = Vector3(nboxx, nboxy, nboxz)

        # we must alocate memory 3d grid and arrays
        self.asm_cells = x86.MemData(num_cells*4)
        self.lin_array = x86.MemData(num_arrays*4 + num_objects * 8 + 4) #we start of index[1] that why extra four bytes
        x86.SetUInt32(self.lin_array.ptr(), 0, 0)
        offset = 4 # offset is in bytes

        self.runtime = runtime = Runtime()

        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    idx = i + nx * j + nx * ny * k
                    cell = self.cells[idx]
                    if len(cell) == 0:
                        adr = self.asm_cells.ptr() 
                        adr = adr + idx * 4
                        x86.SetUInt32(adr, 0, 0)
                    else:
                        adr = self.asm_cells.ptr() 
                        adr = adr + idx * 4
                        x86.SetUInt32(adr, offset, 0)

                        adr = self.lin_array.ptr() 
                        adr += offset
                        num = len(cell)
                        x86.SetUInt32(adr, num, 0)
                        offset += 4

                        lst_address = renmas.interface.objfunc_array(cell, runtime)
                        n = len(lst_address)
                        x86.SetUInt32(adr+4, lst_address, 0)
                        offset = offset + n * 4 


        #br = x86.GetUInt32(self.lin_array.ptr(), 0, 30)
        #print("br", br)
        #for k in range(nz):
        #    for j in range(ny):
        #        for i in range(nx):
        #            idx = i + nx * j + nx * ny * k
        #            adr = self.asm_cells.ptr() 
        #            adr = adr + idx * 4
        #            br = x86.GetUInt32(adr, 0, 0)
        #            print(k, j, i, idx, br)


        print("duzina", max_len)
        print("num objects =", num_objects, " num arrays", num_arrays)
        return None

    def attributes(self):
        d = {}
        bbox = self.bbox
        d["bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0)
        d["bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)
        n_1 = self.n_1
        d["n_1"] = (n_1.x, n_1.y, n_1.z, 0.0) 
        ovn = self.one_overn
        d["one_overn"] = (ovn.x, ovn.y, ovn.z, 0.0)
        nw = self.nbox_width
        d["nbox_width"] = (nw.x, nw.y, nw.z, 0.0)
        d["n"] = (self.nx, self.ny, self.nz, 0)
        d["grid_ptr"] = self.asm_cells.ptr()
        d["arr_ptr"] = self.lin_array.ptr()

        return d

    @classmethod
    def name(cls):
        return "grid"

    @classmethod
    def isect_name(cls):
        return "ray_grid_intersection"

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("grid") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("grid")

    # eax = pointer to ray structure
    # ebx = pointer to grid structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    # TODO - maybe beacuse accept is rare dont't jump on reject - do it opositte jump on accept
    @classmethod
    def isect_asm(cls, runtime, label, populate=True):
        asm_structs = util.structs("ray", "grid", "hitpoint")

        multiple_isect_asm(runtime, "multiple_isect")

        ASM = """
        #DATA
        """
        ASM += asm_structs + """
        float one[4] = 1.0, 1.0, 1.0, 0.0
        float zero[4] = 0.0, 0.0, 0.0, 0.0
        
        int32 ixyz[4]
        float dtxyz[4]

        int32 istep[4]
        int32 istop[4]
        float tnext[4]
        int32 n[4]

        uint32 ones = 0xFFFFFFFF
        float khuge = 999999.999
        uint32 hp_ptr
        uint32 ray_ptr
        uint32 grid_ptr

        #CODE
        """
        ASM += " global " + label + ":\n" 
        if util.AVX:
            ASM += AVX_ASM
        else:
            ASM += SSE_ASM

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_grid_isect" + str(util.unique())
        runtime.load(name, mc)


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

        if dx == 0.0: return False
        a = 1.0 / dx
        if a >= 0:
            tx_min = (x0 - ox) * a
            tx_max = (x1 - ox) * a
        else:
            tx_min = (x1 - ox) * a
            tx_max = (x0 - ox) * a

        if dy == 0.0: return False
        b = 1.0 / dy
        if b >= 0:
            ty_min = (y0 - oy) * b
            ty_max = (y1 - oy) * b
        else:
            ty_min = (y1 - oy) * b
            ty_max = (y0 - oy) * b

        if dz == 0.0: return False
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
                hp = isect(ray, cell)
                if hp and hp.t < tx_next:
                    return hp

                tx_next += dtx
                ix += ix_step
                if ix == ix_stop: return False 
                
            else:
                if ty_next < tz_next:
                    hp = isect(ray, cell)
                    if hp and hp.t < ty_next:
                        return hp

                    ty_next += dty
                    iy += iy_step
                    if iy == iy_stop: return False 
                else:
                    hp = isect(ray, cell)
                    if hp and hp.t < tz_next:
                        return hp

                    tz_next += dtz
                    iz += iz_step
                    if iz == iz_stop: return False 
        return False 



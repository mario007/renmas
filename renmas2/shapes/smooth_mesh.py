
import time
from .hitpoint import HitPoint
from .bbox import BBox
from ..core import Vector3
from .shape import Shape
from .grid_mesh import GridMesh
from ..core import VertexNBuffer, TriangleBuffer 
from .ray_triangle import ray_triangle_intersection

class SmoothMesh(Shape):
    def __init__(self, vb, tb, material):
        if not isinstance(vb, VertexNBuffer):
            raise ValueError("Wrong vertex buffer " + str(type(vb)))
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer " + str(type(tb)))
        self.material = material
        self._vb = vb
        self._tb = tb

        self._grid = GridMesh()
        #start = time.clock()
        self._grid.setup(self)
        #print(time.clock() - start)
        #print(self._grid._show_info())
        bbox = self._grid.bbox
        #print(bbox.x0, bbox.y0, bbox.z0)
        #print(bbox.x1, bbox.y1, bbox.z1)

    def isect_b(self, ray, min_dist=999999.0): #ray direction must be normalized
        hp = self._grid.isect(ray, min_dist)
        if hp:
            return hp.t
        return hp

    # eax = pointer to ray structure
    # ebx = pointer to smooth mesh structure
    # ecx = pointer to minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label, assembler, structures):
        lbl_name = "ray_tri_b" + str(abs(hash(cls)))
        cls._isect_triangles_asm_b(runtimes, lbl_name, assembler, structures)
        GridMesh.isect_asm(runtimes, label, assembler, structures, "smooth_mesh", lbl_name, True)

    def isect(self, ray, min_dist=999999.0): #ray direction must be normalized
        return self._grid.isect(ray, min_dist)

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label, assembler, structures):
        lbl_name = "ray_tri" + str(abs(hash(cls)))
        cls._isect_triangles_asm(runtimes, lbl_name, assembler, structures)
        GridMesh.isect_asm(runtimes, label, assembler, structures, "smooth_mesh", lbl_name)

    def attributes(self):
        d = {}
        d["vertex_buffer_ptr"] = self._vb.addr()
        d["vertex_size"] = self._vb.item_size()
        d["triangle_buffer_ptr"] = self._tb.addr()
        d["triangle_size"] = self._tb.item_size()
        bbox = self._grid.bbox
        d["bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0) 
        d["bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)

        grid = self._grid
        nboxx = float(grid.nx / (bbox.x1 - bbox.x0))
        nboxy = float(grid.ny / (bbox.y1 - bbox.y0))
        nboxz = float(grid.nz / (bbox.z1 - bbox.z0))
        d["nbox_width"] = (nboxx, nboxy, nboxz, 0.0)

        d["n_1"] = (float(grid.nx-1), float(grid.ny-1), float(grid.nz-1), 0.0)
        d["one_overn"] = (1.0 / grid.nx, 1.0 / grid.ny, 1.0 / grid.nz, 0.0)
        d["grid_size"] = (grid.nx, grid.ny, grid.nz, 0)
        d["grid_ptr"] = grid.asm_cells.ptr()
        d["array_ptr"] = grid.lin_array.ptr()

        if self.material is None:
            d["mat_index"] = 999999 #TODO try to solve this in better way 
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def name(cls):
        return "smooth_mesh"

    def bbox(self):
        min_p, max_p = self._vb.bbox()
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1, None)

    def bbox_triangle(self, idx):
        v = self._tb.get(idx)
        if v:
            return self._vb.bbox_triangle(v[0], v[1], v[2])
        return None

    def ntriangles(self):
        return self._tb.size()

    def isect_triangles(self, ray, triangles, min_dist=999999.0):
        hit_point = False 
        for idx in triangles:
            hit = self.ray_triangle(ray, idx, min_dist) 
            if hit is False: continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    # eax = pointer to ray structure
    # ebx = pointer to smooth mesh structure
    # ecx = pointer to minimum distance
    # edx = address in linear grid array --- n:idx1, idx2, ... 
    @classmethod
    def _isect_triangles_asm_b(cls, runtimes, label, assembler, structures):
        code = """
            #DATA
        """
        code += structures.structs(('ray', 'smooth_mesh')) + """
        float epsilon= 0.0005
        float one = 1.0001

        uint32 num_triangles
        uint32 ptr_triangles

        uint32 ptr_ray
        uint32 ptr_smooth_mesh
        uint32 ptr_min_dist

        uint32 isect_ocur 
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov dword [ptr_ray], eax
        mov dword [ptr_smooth_mesh], ebx 
        mov dword [ptr_min_dist], ecx
        mov dword [isect_ocur], 0

        mov esi, dword [edx] ; number of triangles to process
        mov dword [num_triangles], esi
        add edx, 4 ;address of idx triangle array
        mov dword [ptr_triangles], edx

        _triangle_loop:
        mov eax, dword [ptr_ray]
        mov ebx, dword [ptr_smooth_mesh]
        mov ecx, dword [ptr_min_dist]

        
        mov ebp, dword [ptr_triangles]
        mov edx, dword [ebp]
        imul edx, dword [ebx + smooth_mesh.triangle_size]
        add edx, dword [ebx + smooth_mesh.triangle_buffer_ptr]
        
        mov esi, dword [edx]
        mov edi, dword [edx + 4]
        mov ebp, dword [edx + 8]

        imul esi, dword [ebx + smooth_mesh.vertex_size]
        add esi, dword [ebx + smooth_mesh.vertex_buffer_ptr]

        imul edi, dword [ebx + smooth_mesh.vertex_size]
        add edi, dword [ebx + smooth_mesh.vertex_buffer_ptr]

        imul ebp, dword [ebx + smooth_mesh.vertex_size]
        add ebp, dword [ebx + smooth_mesh.vertex_buffer_ptr]

        ; eax - ray, ebx - smooth mesh, ecx - distance, esi - p0, edi - p1, ebp - p2
        ;call ray_triangle_function
        """
        code += ray_triangle_intersection() + """
        cmp eax, 0
        je _next_triangle
        ; intersection ocur, t = xmm6
        mov dword [isect_ocur], 1
        ; update distance
        macro eq32 ecx = xmm6 {xmm0}

        _next_triangle:
        add dword [ptr_triangles], 4
        sub dword [num_triangles], 1  
        jnz _triangle_loop
        
        ;result
        mov eax, dword [isect_ocur]
        cmp eax, 0
        je _end_intersections

        mov ecx, dword [ptr_min_dist]
        macro eq32 xmm0 = ecx

        _end_intersections:
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangles_isects_b" + str(hash(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)


    # eax = pointer to ray structure
    # ebx = pointer to smooth mesh structure
    # ecx = pointer to minimum distance
    # edx = address in linear grid array --- n:idx1, idx2, ... 
    @classmethod
    def _isect_triangles_asm(cls, runtimes, label, assembler, structures):

        code = """
            #DATA
        """
        code += structures.structs(('ray', 'smooth_mesh')) + """
        float epsilon= 0.0005
        float one = 1.0001

        uint32 num_triangles
        uint32 ptr_triangles

        uint32 ptr_ray
        uint32 ptr_smooth_mesh
        uint32 ptr_min_dist

        float tmp_normal[4]
        uint32 isect_ocur 
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov dword [ptr_ray], eax
        mov dword [ptr_smooth_mesh], ebx 
        mov dword [ptr_min_dist], ecx
        mov dword [isect_ocur], 0

        mov esi, dword [edx] ; number of triangles to process
        mov dword [num_triangles], esi
        add edx, 4 ;address of idx triangle array
        mov dword [ptr_triangles], edx

        _triangle_loop:
        mov eax, dword [ptr_ray]
        mov ebx, dword [ptr_smooth_mesh]
        mov ecx, dword [ptr_min_dist]

        
        mov ebp, dword [ptr_triangles]
        mov edx, dword [ebp]
        imul edx, dword [ebx + smooth_mesh.triangle_size]
        add edx, dword [ebx + smooth_mesh.triangle_buffer_ptr]
        
        mov esi, dword [edx]
        mov edi, dword [edx + 4]
        mov ebp, dword [edx + 8]

        imul esi, dword [ebx + smooth_mesh.vertex_size]
        add esi, dword [ebx + smooth_mesh.vertex_buffer_ptr]

        imul edi, dword [ebx + smooth_mesh.vertex_size]
        add edi, dword [ebx + smooth_mesh.vertex_buffer_ptr]

        imul ebp, dword [ebx + smooth_mesh.vertex_size]
        add ebp, dword [ebx + smooth_mesh.vertex_buffer_ptr]

        ; eax - ray, ebx - smooth mesh, ecx - distance, esi - p0, edi - p1, ebp - p2
        ;call ray_triangle_function
        """
        code += ray_triangle_intersection() + """
        cmp eax, 0
        je _next_triangle
        ; intersection ocur, t = xmm6, gamma = xmm5, beta = xmm2 
        mov dword [isect_ocur], 1
        ; update distance
        macro eq32 ecx = xmm6 {xmm0}

        ; calculate normal
        add esi, 16
        macro eq128 xmm0 = esi
        add edi, 16
        macro eq128 xmm1 = edi
        add ebp, 16
        macro eq128 xmm3 = ebp
        macro eq32 xmm4 = one - xmm5 - xmm2
        macro broadcast xmm4 = xmm4[0]
        macro eq128 xmm4 = xmm4 * xmm0
        macro broadcast xmm2 = xmm2[0]
        macro eq128 xmm2 = xmm2 * xmm1
        macro broadcast xmm5 = xmm5[0]
        macro eq128 xmm5 = xmm5 * xmm3
        macro eq128 xmm4 = xmm4 + xmm2 + xmm5
        macro normalization xmm4 {xmm6, xmm7} 
        macro eq128 tmp_normal = xmm4 {xmm0}

        _next_triangle:
        add dword [ptr_triangles], 4
        sub dword [num_triangles], 1  
        jnz _triangle_loop
        
        ;result
        mov eax, dword [isect_ocur]
        cmp eax, 0
        je _end_intersections

        mov edx, dword [ptr_ray]
        mov ecx, dword [ptr_min_dist]
        macro eq32 xmm0 = ecx
        macro broadcast xmm0 = xmm0[0]
        macro eq128 xmm1 = xmm0 * edx.ray.dir + edx.ray.origin
        macro eq128 xmm2 = tmp_normal

        _end_intersections:
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangles_isects" + str(hash(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)


    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 = self._tb.get(idx)
        p0,n0 = self._vb.get(v0)
        p1,n1 = self._vb.get(v1)
        p2,n2 = self._vb.get(v2)

        a = p0[0] - p1[0]
        b = p0[0] - p2[0] 
        c = ray.dir.x
        d = p0[0] - ray.origin.x
        e = p0[1] - p1[1]
        f = p0[1] - p2[1]
        g = ray.dir.y
        h = p0[1] - ray.origin.y
        i = p0[2] - p1[2] 
        j = p0[2] - p2[2]
        k = ray.dir.z
        l = p0[2] - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)
        if temp3 == 0.0: return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0: return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0: return False

        if beta + gamma > 1.0: return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001: return False # self-intersection

        hit_point = ray.origin + ray.dir * t

        normal0 = Vector3(n0[0], n0[1], n0[2])
        normal1 = Vector3(n1[0], n1[1], n1[2])
        normal2 = Vector3(n2[0], n2[1], n2[2])

        normal = normal0 * (1.0 - beta - gamma) + beta * normal1 + gamma * normal2  
        normal.normalize()

        return HitPoint(t, hit_point, normal, self.material, ray)



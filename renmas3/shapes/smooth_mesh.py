
import platform
from ..base import Ray, Vector3
from ..base import VertexNBuffer, TriangleBuffer
from .base_mesh import BaseMesh
from .grid_mesh import GridMesh
from .bbox import BBox

class SmoothMesh(BaseMesh):
    def __init__(self, vb, tb, material_idx=0):
        super(SmoothMesh, self).__init__()

        if not isinstance(vb, VertexNBuffer):
            raise ValueError("Wrong vertex buffer", vb)
        if not isinstance(tb, TriangleBuffer):
            raise ValueError("Wrong triangle buffer", tb)

        self._vb = vb
        self._tb = tb
        self.material_idx = material_idx

        self._grid = GridMesh()
        self._grid.setup(self)

    def bbox(self):
        min_p, max_p = self._vb.bbox()
        p0 = Vector3(min_p[0], min_p[1], min_p[2])
        p1 = Vector3(max_p[0], max_p[1], max_p[2])
        return BBox(p0, p1)

    def ntriangles(self):
        return self._tb.size()

    @classmethod
    def has_uv(cls):
        return False

    @classmethod
    def has_normals(cls):
        return True

    def get_indices(self, idx):
        return self._tb.get(idx)

    def get_point(self, idx):
        return self._vb.get(idx)[0]
    
    def get_normal(self, idx):
        return self._vb.get(idx)[1]

    def isect(self, ray, min_dist=999999.0): #ray direction must be normalized
        return self._grid.isect(ray, min_dist)

    def isect_b(self, ray, min_dist=999999.0): #ray direction must be normalized
        hp = self._grid.isect(ray, min_dist)
        if hp:
            return hp.t
        return hp

    def bbox_triangle(self, idx):
        v = self._tb.get(idx)
        if v:
            return self._vb.bbox_triangle(v[0], v[1], v[2])
        return None

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
        d["material_idx"] = self.material_idx
        return d

    @classmethod
    def populate_ds(cls, ds, mesh, name):
        ds[name + ".vertex_buffer_ptr"] = mesh._vb.addr()
        ds[name + ".vertex_size"] = mesh._vb.item_size()
        ds[name + ".triangle_buffer_ptr"] = mesh._tb.addr()
        ds[name + ".triangle_size"] = mesh._tb.item_size()
        bbox = mesh._grid.bbox
        ds[name + ".bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0) 
        ds[name + ".bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)

        grid = mesh._grid
        nboxx = float(grid.nx / (bbox.x1 - bbox.x0))
        nboxy = float(grid.ny / (bbox.y1 - bbox.y0))
        nboxz = float(grid.nz / (bbox.z1 - bbox.z0))
        ds[name + ".nbox_width"] = (nboxx, nboxy, nboxz, 0.0)

        ds[name + ".n_1"] = (float(grid.nx-1), float(grid.ny-1), float(grid.nz-1), 0.0)
        ds[name + ".one_overn"] = (1.0 / grid.nx, 1.0 / grid.ny, 1.0 / grid.nz, 0.0)
        ds[name + ".grid_size"] = (grid.nx, grid.ny, grid.nz, 0)
        ds[name + ".grid_ptr"] = grid.asm_cells.ptr()
        ds[name + ".array_ptr"] = grid.lin_array.ptr()
        ds[name + ".material_idx"] = mesh.material_idx

    @classmethod
    def asm_struct_name(cls):
        return "SmoothMesh"

    @classmethod
    def asm_struct(cls):
        bits = platform.architecture()[0]
        if bits == '64bit':
            code = """
                struct SmoothMesh
                uint64 vertex_buffer_ptr
                uint32 vertex_size
                uint64 triangle_buffer_ptr
                uint32 triangle_size
                uint32 material_idx
                float bbox_min[4]
                float bbox_max[4]
                float nbox_width[4]
                float n_1[4]
                float one_overn[4]
                int32 grid_size[4]
                uint64 grid_ptr
                uint64 array_ptr
                end struct
            """
        else:
            code = """
                struct SmoothMesh
                uint32 vertex_buffer_ptr
                uint32 vertex_size
                uint32 triangle_buffer_ptr
                uint32 triangle_size
                uint32 material_idx
                float bbox_min[4]
                float bbox_max[4]
                float nbox_width[4]
                float n_1[4]
                float one_overn[4]
                int32 grid_size[4]
                uint32 grid_ptr
                uint32 array_ptr
                end struct
            """
        return code

    @classmethod
    def isect_triangles_asm_32(cls, label, ray_isect_label):
        code = """
            #DATA
        """
        code += Ray.asm_struct()
        code += cls.asm_struct()
        epsilon = "float epsilon = %f\n" % cls.epsilon()
        code += epsilon + """
        uint32 num_triangles
        uint32 ptr_triangles, ptr_ray, ptr_flat_mesh, ptr_min_dist
        uint32 isect_ocur 

        float one = 1.0
        float _n0[4]
        float _n1[4]
        float _n2[4]
        float _beta, _gamma
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov dword [ptr_ray], eax
        mov dword [ptr_flat_mesh], ebx 
        mov dword [ptr_min_dist], ecx
        mov dword [isect_ocur], 0

        mov esi, dword [edx] ; number of triangles to process
        mov dword [num_triangles], esi
        add edx, 4 ;address of idx triangle array
        mov dword [ptr_triangles], edx

        _triangle_loop:
        mov eax, dword [ptr_ray]
        mov ebx, dword [ptr_flat_mesh]
        
        mov ebp, dword [ptr_triangles]
        mov edx, dword [ebp]
        imul edx, dword [ebx + SmoothMesh.triangle_size]
        add edx, dword [ebx + SmoothMesh.triangle_buffer_ptr]
        
        mov esi, dword [edx]
        mov edi, dword [edx + 4]
        mov ebp, dword [edx + 8]

        imul esi, dword [ebx + SmoothMesh.vertex_size]
        add esi, dword [ebx + SmoothMesh.vertex_buffer_ptr]

        imul edi, dword [ebx + SmoothMesh.vertex_size]
        add edi, dword [ebx + SmoothMesh.vertex_buffer_ptr]

        imul ebp, dword [ebx + SmoothMesh.vertex_size]
        add ebp, dword [ebx + SmoothMesh.vertex_buffer_ptr]

        ;eax - ray, ebx - Flat Mesh, esi - p0, edi - p1, ebp - p2
        macro eq128 xmm3 = eax.Ray.origin
        macro eq128 xmm4 = eax.Ray.dir
        macro eq128 xmm5 = esi
        macro eq128 xmm6 = edi
        macro eq128 xmm7 = ebp
        ;call ray_triangle_function
        """
        code += "call " + ray_isect_label + """
        cmp eax, 0
        je _next_triangle
        mov ecx, dword [ptr_min_dist]
        macro if xmm0 > ecx goto _next_triangle

        ; intersection ocur, t = xmm0
        mov dword [isect_ocur], 1

        ; update distance
        macro eq32 ecx = xmm0 {xmm7}

        ; save for calculation of normal
        macro eq32 _beta = xmm1 {xmm7}
        macro eq32 _gamma = xmm2 {xmm7}
        add esi, 16
        add edi, 16
        add ebp, 16
        macro eq128 xmm0 = esi
        macro eq128 xmm1 = edi
        macro eq128 xmm2 = ebp
        macro eq128 _n0 = xmm0 {xmm7}
        macro eq128 _n1 = xmm1 {xmm7}
        macro eq128 _n2 = xmm2 {xmm7}

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
        macro eq128 xmm1 = xmm0 * edx.Ray.dir + edx.Ray.origin

        ;calculation of normal
        macro eq32 xmm2 = one - _beta - _gamma
        macro broadcast xmm2 = xmm2[0]
        macro eq128 xmm2 = xmm2 * _n0
        macro eq32 xmm3 = _beta
        macro broadcast xmm3 = xmm3[0]
        macro eq128 xmm3 = xmm3 * _n1
        macro eq32 xmm4 = _gamma
        macro broadcast xmm4 = xmm4[0]
        macro eq128 xmm4 = xmm4 * _n2
        macro eq128 xmm2 = xmm2 + xmm3 + xmm4
        macro normalization xmm2 {xmm6, xmm7} 

        _end_intersections:
        ret
        """
        return code

    @classmethod
    def isect_triangles_asm_64(cls, label, ray_isect_label):
        code = """
            #DATA
        """
        code += Ray.asm_struct()
        code += cls.asm_struct()
        epsilon = "float epsilon = %f\n" % cls.epsilon()
        code += epsilon + """
        uint32 num_triangles
        uint64 ptr_triangles, ptr_ray, ptr_flat_mesh, ptr_min_dist
        uint32 isect_ocur 

        float one = 1.0
        float _n0[4]
        float _n1[4]
        float _n2[4]
        float _beta, _gamma
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov qword [ptr_ray], rax
        mov qword [ptr_flat_mesh], rbx 
        mov qword [ptr_min_dist], rcx
        mov dword [isect_ocur], 0

        mov esi, dword [rdx] ; number of triangles to process
        mov dword [num_triangles], esi
        add rdx, 4 ;address of idx triangle array
        mov qword [ptr_triangles], rdx

        _triangle_loop:
        mov rax, qword [ptr_ray]
        mov rbx, qword [ptr_flat_mesh]
        
        mov rbp, qword [ptr_triangles]
        mov edx, dword [rbp]

        imul edx, dword [rbx + SmoothMesh.triangle_size]
        add rdx, qword [rbx + SmoothMesh.triangle_buffer_ptr]
        
        mov esi, dword [rdx]
        mov edi, dword [rdx + 4]
        mov ebp, dword [rdx + 8]

        imul esi, dword [rbx + SmoothMesh.vertex_size]
        add rsi, qword [rbx + SmoothMesh.vertex_buffer_ptr]

        imul edi, dword [rbx + SmoothMesh.vertex_size]
        add rdi, qword [rbx + SmoothMesh.vertex_buffer_ptr]

        imul ebp, dword [rbx + SmoothMesh.vertex_size]
        add rbp, qword [rbx + SmoothMesh.vertex_buffer_ptr]

        ;eax - ray, ebx - Flat Mesh, esi - p0, edi - p1, ebp - p2
        macro eq128 xmm3 = eax.Ray.origin
        macro eq128 xmm4 = eax.Ray.dir
        macro eq128 xmm5 = rsi
        macro eq128 xmm6 = rdi
        macro eq128 xmm7 = rbp
        ;call ray_triangle_function
        """
        code += "call " + ray_isect_label + """
        cmp eax, 0
        je _next_triangle
        mov rcx, qword [ptr_min_dist]
        macro if xmm0 > rcx goto _next_triangle

        ; intersection ocur, t = xmm0
        mov dword [isect_ocur], 1

        ; update distance
        macro eq32 ecx = xmm0 {xmm7}

        ; save for calculation of normal
        macro eq32 _beta = xmm1 {xmm7}
        macro eq32 _gamma = xmm2 {xmm7}
        add rsi, 16
        add rdi, 16
        add rbp, 16
        macro eq128 xmm0 = rsi
        macro eq128 xmm1 = rdi
        macro eq128 xmm2 = rbp
        macro eq128 _n0 = xmm0 {xmm7}
        macro eq128 _n1 = xmm1 {xmm7}
        macro eq128 _n2 = xmm2 {xmm7}

        _next_triangle:
        add qword [ptr_triangles], 4
        sub dword [num_triangles], 1  
        jnz _triangle_loop
        
        ;result
        mov eax, dword [isect_ocur]
        cmp eax, 0
        je _end_intersections

        mov rdx, qword [ptr_ray]
        mov rcx, qword [ptr_min_dist]
        macro eq32 xmm0 = rcx
        macro broadcast xmm0 = xmm0[0]
        macro eq128 xmm1 = xmm0 * edx.Ray.dir + edx.Ray.origin

        ;calculation of normal
        macro eq32 xmm2 = one - _beta - _gamma
        macro broadcast xmm2 = xmm2[0]
        macro eq128 xmm2 = xmm2 * _n0
        macro eq32 xmm3 = _beta
        macro broadcast xmm3 = xmm3[0]
        macro eq128 xmm3 = xmm3 * _n1
        macro eq32 xmm4 = _gamma
        macro broadcast xmm4 = xmm4[0]
        macro eq128 xmm4 = xmm4 * _n2
        macro eq128 xmm2 = xmm2 + xmm3 + xmm4
        macro normalization xmm2 {xmm6, xmm7} 

        _end_intersections:
        ret
        """
        return code

    @classmethod
    def isect_triangles_asm_b_32(cls, label, ray_isect_label):
        code = """
            #DATA
        """
        code += Ray.asm_struct()
        code += cls.asm_struct()
        epsilon = "float epsilon = %f\n" % cls.epsilon()
        code += epsilon + """
        uint32 num_triangles
        uint32 ptr_triangles, ptr_ray, ptr_flat_mesh, ptr_min_dist
        uint32 isect_ocur 
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov dword [ptr_ray], eax
        mov dword [ptr_flat_mesh], ebx 
        mov dword [ptr_min_dist], ecx
        mov dword [isect_ocur], 0

        mov esi, dword [edx] ; number of triangles to process
        mov dword [num_triangles], esi
        add edx, 4 ;address of idx triangle array
        mov dword [ptr_triangles], edx

        _triangle_loop:
        mov eax, dword [ptr_ray]
        mov ebx, dword [ptr_flat_mesh]
        
        mov ebp, dword [ptr_triangles]
        mov edx, dword [ebp]
        imul edx, dword [ebx + SmoothMesh.triangle_size]
        add edx, dword [ebx + SmoothMesh.triangle_buffer_ptr]
        
        mov esi, dword [edx]
        mov edi, dword [edx + 4]
        mov ebp, dword [edx + 8]

        imul esi, dword [ebx + SmoothMesh.vertex_size]
        add esi, dword [ebx + SmoothMesh.vertex_buffer_ptr]

        imul edi, dword [ebx + SmoothMesh.vertex_size]
        add edi, dword [ebx + SmoothMesh.vertex_buffer_ptr]

        imul ebp, dword [ebx + SmoothMesh.vertex_size]
        add ebp, dword [ebx + SmoothMesh.vertex_buffer_ptr]

        ;eax - ray, ebx - Flat Mesh, esi - p0, edi - p1, ebp - p2
        macro eq128 xmm3 = eax.Ray.origin
        macro eq128 xmm4 = eax.Ray.dir
        macro eq128 xmm5 = esi
        macro eq128 xmm6 = edi
        macro eq128 xmm7 = ebp
        ;call ray_triangle_function
        """
        code += "call " + ray_isect_label + """
        cmp eax, 0
        je _next_triangle
        mov ecx, dword [ptr_min_dist]
        macro if xmm0 > ecx goto _next_triangle

        ; intersection ocur, t = xmm0
        mov dword [isect_ocur], 1

        ; update distance
        macro eq32 ecx = xmm0 {xmm7}

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
        return code

    @classmethod
    def isect_triangles_asm_b_64(cls, label, ray_isect_label):
        code = """
            #DATA
        """
        code += Ray.asm_struct()
        code += cls.asm_struct()
        epsilon = "float epsilon = %f\n" % cls.epsilon()
        code += epsilon + """
        uint32 num_triangles
        uint64 ptr_triangles, ptr_ray, ptr_flat_mesh, ptr_min_dist
        uint32 isect_ocur 
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov qword [ptr_ray], rax
        mov qword [ptr_flat_mesh], rbx 
        mov qword [ptr_min_dist], rcx
        mov dword [isect_ocur], 0

        mov esi, dword [rdx] ; number of triangles to process
        mov dword [num_triangles], esi
        add rdx, 4 ;address of idx triangle array
        mov qword [ptr_triangles], rdx

        _triangle_loop:
        mov rax, qword [ptr_ray]
        mov rbx, qword [ptr_flat_mesh]
        
        mov rbp, qword [ptr_triangles]
        mov edx, dword [rbp]
        imul edx, dword [rbx + SmoothMesh.triangle_size]
        add rdx, qword [rbx + SmoothMesh.triangle_buffer_ptr]
        
        mov esi, dword [rdx]
        mov edi, dword [rdx + 4]
        mov ebp, dword [rdx + 8]

        imul esi, dword [rbx + SmoothMesh.vertex_size]
        add rsi, qword [rbx + SmoothMesh.vertex_buffer_ptr]

        imul edi, dword [rbx + SmoothMesh.vertex_size]
        add rdi, qword [rbx + SmoothMesh.vertex_buffer_ptr]

        imul ebp, dword [rbx + SmoothMesh.vertex_size]
        add rbp, qword [rbx + SmoothMesh.vertex_buffer_ptr]

        ;rax - ray, ebx - Flat Mesh, rsi - p0, rdi - p1, rbp - p2
        macro eq128 xmm3 = eax.Ray.origin
        macro eq128 xmm4 = eax.Ray.dir
        macro eq128 xmm5 = rsi
        macro eq128 xmm6 = rdi
        macro eq128 xmm7 = rbp
        ;call ray_triangle_function
        """
        code += "call " + ray_isect_label + """
        cmp eax, 0
        je _next_triangle
        mov rcx, qword [ptr_min_dist]
        macro if xmm0 > rcx goto _next_triangle

        ; intersection ocur, t = xmm0
        mov dword [isect_ocur], 1

        ; update distance
        macro eq32 ecx = xmm0 {xmm7}

        _next_triangle:
        add qword [ptr_triangles], 4
        sub dword [num_triangles], 1  
        jnz _triangle_loop
        
        ;result
        mov eax, dword [isect_ocur]
        cmp eax, 0
        je _end_intersections

        mov rcx, qword [ptr_min_dist]
        macro eq32 xmm0 = ecx

        _end_intersections:
        ret
        """
        return code


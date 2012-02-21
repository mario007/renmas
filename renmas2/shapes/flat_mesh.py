
import time
from .hitpoint import HitPoint
from .bbox import BBox
from ..core import Vector3
from .shape import Shape
from .grid_mesh import GridMesh
from ..core import VertexBuffer, TriangleBuffer 

class FlatMesh(Shape):
    def __init__(self, vb, tb, material):
        if not isinstance(vb, VertexBuffer):
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

    def isect(self, ray, min_dist=999999.0): #ray direction must be normalized
        return self._grid.isect(ray, min_dist)

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label, assembler, structures):
        pass

    def attributes(self):
        d = {}
        d["vertex_buffer_ptr"] = self._vb.addr()
        d["triangle_buffer_ptr"] = self._tb.addr()
        if self.material is None:
            d["mat_index"] = 999999 #TODO try to solve this in better way 
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def name(cls):
        return "flat_mesh"

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
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = address in linear grid array --- n:idx1, idx2, ... 
    @classmethod
    def _isect_triangles_asm(cls, runtimes, label, assembler, structures):

        code = """
            #DATA
        """
        code += structures.structs(('ray', 'flat_mesh')) + """
        float epsilon= 0.00001
        float one = 1.0
        uint32 num_triangles
        uint32 addr_idx
        #CODE
        """
        code += " global " + label + ":\n" + """
        mov esi, dword [edx] ; number of triangles to process
        mov dword [num_triangles], esi
        add edx, 4 ;address of idx triangle array
        mov dword [addr_idx], edx

        _triangle_loop:
        ; load points
        mov ebp, dword [ebx + flat_mesh.triangle_buffer_ptr]
        mov edx, dword [addr_idx]


        ; prepare arguments
        ;call ray_triangle_function

        add dword [addr_idx], 4
        sub dword [num_triangles], 1  
        jnz _triangle_loop
        
        ;result

        ret
        """

    # eax = pointer to ray structure
    # ecx = pointer to minimum distance

    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 = self._tb.get(idx)
        p0 = self._vb.get(v0)
        p1 = self._vb.get(v1)
        p2 = self._vb.get(v2)

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

        normal0 = Vector3(p0[0], p0[1], p0[2])
        normal1 = Vector3(p1[0], p1[1], p1[2])
        normal2 = Vector3(p2[0], p2[1], p2[2])
        normal = (normal1 - normal0).cross(normal2 - normal0)
        normal.normalize()

        return HitPoint(t, hit_point, normal, self.material, ray)


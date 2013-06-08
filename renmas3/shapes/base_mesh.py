
import platform
from ..base import Ray, Vector3
from ..macros import create_assembler
from .hit import HitPoint
from .shape import Shape
from .grid_mesh import GridMesh
from .ray_triangle import ray_triangle_intersection

class BaseMesh(Shape):

    def ntriangles(self):
        raise NotImplementedError()

    def bbox_triangle(self, idx):
        raise NotImplementedError()

    def isect_triangles(self, ray, triangles, min_dist=999999.0):
        hit_point = False 
        for idx in triangles:
            hit = self.ray_triangle(ray, idx, min_dist) 
            if hit is False: continue
            if hit.t < min_dist:
                min_dist = hit.t
                hit_point = hit
        return hit_point

    def get_point(self, idx):
        raise NotImplementedError()

    def get_normal(self, idx):
        raise NotImplementedError()

    def get_indices(self, idx):
        raise NotImplementedError()

    def get_uv(self, idx):
        raise NotImplementedError()

    @classmethod
    def has_normals(cls):
        raise NotImplementedError()

    @classmethod
    def has_uv(cls):
        raise NotImplementedError()

    def ray_triangle(self, ray, idx, min_dist = 999999.0):
        v0, v1, v2 = self.get_indices(idx)
        p0 = self.get_point(v0)
        p1 = self.get_point(v1)
        p2 = self.get_point(v2)
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

        if t < 0.0001: return False # self-intersection

        hit_point = ray.origin + ray.dir * t
        
        if self.has_normals():
            n0 = self.get_normal(v0)
            n1 = self.get_normal(v1)
            n2 = self.get_normal(v2)

            normal0 = Vector3(n0[0], n0[1], n0[2])
            normal1 = Vector3(n1[0], n1[1], n1[2])
            normal2 = Vector3(n2[0], n2[1], n2[2])

            normal = normal0 * (1.0 - beta - gamma) + beta * normal1 + gamma * normal2  
            normal.normalize()
        else:
            normal0 = Vector3(p0[0], p0[1], p0[2])
            normal1 = Vector3(p1[0], p1[1], p1[2])
            normal2 = Vector3(p2[0], p2[1], p2[2])
            normal = (normal1 - normal0).cross(normal2 - normal0)
            normal.normalize()

        u = v = 0.0
        if self.has_uv():
            uv0 = self.get_uv(v0)
            uv1 = self.get_uv(v1)
            uv2 = self.get_uv(v2)
            u = uv0[0] * (1.0 - beta - gamma) + beta * uv1[0] + gamma * uv2[0]
            v = uv0[1] * (1.0 - beta - gamma) + beta * uv1[1] + gamma * uv2[1]

        return HitPoint(t, hit_point, normal, self.material_idx, u=u, v=v)

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label):
        lbl_name = "ray_tri" + str(id(cls))
        cls.isect_triangles_asm(runtimes, lbl_name)
        GridMesh.isect_asm(runtimes, label, cls.asm_struct_name(),
                cls.asm_struct(), lbl_name, uv=cls.has_uv())

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label):
        lbl_name = "ray_tri_b" + str(id(cls))
        cls.isect_triangles_asm_b(runtimes, lbl_name)
        GridMesh.isect_asm(runtimes, label, cls.asm_struct_name(), cls.asm_struct(), lbl_name, visibility=True)

    @classmethod
    def ray_triangle_isect_asm(cls, runtimes, prefix):
        assembler = create_assembler()
        ray_isect_label = prefix + str(id(cls))
        code = ray_triangle_intersection(ray_isect_label)
        for r in runtimes:
            if not r.global_exists(ray_isect_label):
                mc = assembler.assemble(code, True)
                r.load(ray_isect_label, mc)

        return ray_isect_label

    @classmethod
    def epsilon(cls):
        return 0.0005

    # eax, rax = pointer to ray structure
    # ebx, rbx = pointer to flat mesh structure
    # ecx, rcx = pointer to minimum distance
    # edx, rdx = address in linear grid array --- n:idx1, idx2, ... 
    @classmethod
    def isect_triangles_asm(cls, runtimes, label):
        bits = platform.architecture()[0]
        bit64 = True if bits == "64bit" else False
        ray_isect_label = cls.ray_triangle_isect_asm(runtimes, "ray_triangle_isect")

        if bit64:
            code = cls.isect_triangles_asm_64(label, ray_isect_label)
        else:
            code = cls.isect_triangles_asm_32(label, ray_isect_label)
        
        assembler = create_assembler()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangles_isects" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    @classmethod
    def isect_triangles_asm_32(cls, label, ray_isect_label):
        raise NotImplementedError()

    @classmethod
    def isect_triangles_asm_64(cls, label, ray_isect_label):
        raise NotImplementedError()

    # eax = pointer to ray structure
    # ebx = pointer to flat mesh structure
    # ecx = pointer to minimum distance
    # edx = address in linear grid array --- n:idx1, idx2, ... 
    @classmethod
    def isect_triangles_asm_b(cls, runtimes, label):
        bits = platform.architecture()[0]
        bit64 = True if bits == "64bit" else False
        ray_isect_label = cls.ray_triangle_isect_asm(runtimes, "ray_triangle_isect")

        if bit64:
            code = cls.isect_triangles_asm_b_64(label, ray_isect_label)
        else:
            code = cls.isect_triangles_asm_b_32(label, ray_isect_label)

        assembler = create_assembler()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangles_isects_b" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    @classmethod
    def isect_triangles_asm_b_32(cls, label, ray_isect_label):
        raise NotImplementedError()

    @classmethod
    def isect_triangles_asm_b_64(cls, label, ray_isect_label):
        raise NotImplementedError()

    def __getstate__(self):
        return {}


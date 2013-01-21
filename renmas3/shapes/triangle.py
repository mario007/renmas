import platform

import renmas3.switch as proc

from ..base import Ray
from ..macros import create_assembler
from .hit import HitPoint
from .shape import Shape

from .ray_triangle import ray_triangle_intersection

class Triangle(Shape):
    __slots__ = ['v0', 'v1', 'v2', 'material_idx','normal', 'n0',
            'n1', 'n2', 'tu0', 'tv0', 'tu1', 'tv1', 'tu2', 'tv2', 'has_normals',
            'has_uv']
    def __init__(self, v0, v1, v2, material_idx=0, n0=None, n1=None, n2=None,
            tu0=None, tv0=None, tu1=None, tv1=None, tu2=None, tv2=None):

        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material_idx = material_idx
        self.normal = None
        self.n0 = n0
        self.n1 = n1
        self.n2 = n2
        self.tu0 = tu0
        self.tv0 = tv0
        self.tu1 = tu1
        self.tv1 = tv1
        self.tu2 = tu2
        self.tv2 = tv2

        if n0 is None or n1 is None or n2 is None:
            self.normal = (v1 - v0).cross(v2 - v0)
            self.normal.normalize()
            self.has_normals = False 
        else:
            self.n0.normalize()
            self.n1.normalize()
            self.n2.normalize()
            self.has_normals = True 

        if self.tu0 is not None: # we must also calculate texture coordinates
            self.has_uv = True
        else:
            self.has_uv = False

    def isect_b(self, ray, min_dist=99999.0): #ray direction must be normalized
        a = self.v0.x - self.v1.x
        b = self.v0.x - self.v2.x
        c = ray.dir.x 
        d = self.v0.x - ray.origin.x
        e = self.v0.y - self.v1.y
        f = self.v0.y - self.v2.y
        g = ray.dir.y
        h = self.v0.y - ray.origin.y
        i = self.v0.z - self.v1.z
        j = self.v0.z - self.v2.z
        k = ray.dir.z
        l = self.v0.z - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)

        if temp3 == 0.0:
            return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0:
            return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0:
            return False

        if beta + gamma > 1.0:
            return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001:
            return False # self-intersection
        if t > min_dist:
            return False
        return t

    def isect(self, ray, min_dist=99999.0): #ray direction must be normalized

        a = self.v0.x - self.v1.x
        b = self.v0.x - self.v2.x
        c = ray.dir.x 
        d = self.v0.x - ray.origin.x
        e = self.v0.y - self.v1.y
        f = self.v0.y - self.v2.y
        g = ray.dir.y
        h = self.v0.y - ray.origin.y
        i = self.v0.z - self.v1.z
        j = self.v0.z - self.v2.z
        k = ray.dir.z
        l = self.v0.z - ray.origin.z

        m = f * k - g * j
        n = h * k - g * l
        p = f * l - h * j
        q = g * i - e * k
        s = e * j - f * i

        temp3 =  (a * m + b * q + c * s)

        if temp3 == 0.0:
            return False
        inv_denom = 1.0 / temp3

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0:
            return False

        r = e * l - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0:
            return False

        if beta + gamma > 1.0:
            return False

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < 0.00001:
            return False # self-intersection

        if t > min_dist:
            return False

        hit_point = ray.origin + ray.dir * t
        if self.has_normals: # interpolate normal
            n0 = (1.0 - beta - gamma) * self.n0
            n1 = beta * self.n1
            n2 = gamma * self.n2
            normal = n0 + n1 + n2
            normal.normalize()
        else:
            normal = self.normal
        
        if self.has_uv: # we must also calculate texture coordinates
            alpha = 1.0 - beta - gamma
            u = alpha * self.tu0 + beta * self.tu1 + gamma * self.tu2
            v = alpha * self.tv0 + beta * self.tv1 + gamma * self.tv2
        else:
            u = 0.0
            v = 0.0

        return HitPoint(t, hit_point, normal, self.material_idx, u, v)

    @classmethod
    def asm_struct(cls):
        tri = """
            struct Triangle
            float v0[4]
            float v1[4]
            float v2[4]

            float normal[4]
            float n0[4]
            float n1[4]
            float n2[4]

            float tu0, tu1, tu2
            float tv0, tv1, tv2

            int32 material_idx
            int32 has_normals
            int32 has_uv
            end struct

        """
        return tri 

    def attributes(self):
        d = {}
        d["v0"] = self.v0.to_ds()
        d["v1"] = self.v1.to_ds()
        d["v2"] = self.v2.to_ds()
        if self.has_normals:
            d["n0"] = self.n0.to_ds()
            d["n1"] = self.n1.to_ds()
            d["n2"] = self.n2.to_ds()
        else:
            d["normal"] = self.normal.to_ds()

        if self.has_uv:
            d["tu0"] = self.tu0
            d["tu1"] = self.tu1
            d["tu2"] = self.tu2
            d["tv0"] = self.tv0
            d["tv1"] = self.tv1
            d["tv2"] = self.tv2
            d["has_uv"] = 1
        else:
            d["has_uv"] = 0
        d["material_idx"] = self.material_idx
        if self.has_normals:
            d["has_normals"] = 1
        else:
            d["has_normals"] = 0
        return d

    # eax = pointer to ray structure
    # ebx = pointer to triangle structure
    # ecx = minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label):
        assembler = create_assembler()
        ray_isect_label = "ray_triangle_isect_b" + str(id(cls))
        code = ray_triangle_intersection(ray_isect_label)
        for r in runtimes:
            if not r.global_exists(ray_isect_label):
                mc = assembler.assemble(code, True)
                r.load(ray_isect_label, mc)
        
        code = """
            #DATA
        """
        code += Ray.asm_struct()
        code += Triangle.asm_struct()
        code += " #CODE \n"
        code += " global " + label + ":\n" + """
        macro eq128 xmm3 = eax.Ray.origin
        macro eq128 xmm4 = eax.Ray.dir
        macro eq128 xmm5 = ebx.Triangle.v0
        macro eq128 xmm6 = ebx.Triangle.v1
        macro eq128 xmm7 = ebx.Triangle.v2
        macro push ecx
        """
        code += "call %s\n" % ray_isect_label
        code += """
        macro pop ecx
        cmp eax, 0
        jne _maybe_accept
        ret
        _maybe_accept:
        macro if xmm0 < ecx goto _accept
        xor eax, eax
        ret
        _accept:
        ret
        """
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangle_intersection_bool" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    # eax = pointer to ray structure
    # ebx = pointer to triangle structure
    # ecx = minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label):
        assembler = create_assembler()
        ray_isect_label = "ray_triangle_isect" + str(id(cls))
        code = ray_triangle_intersection(ray_isect_label)
        for r in runtimes:
            if not r.global_exists(ray_isect_label):
                mc = assembler.assemble(code, True)
                r.load(ray_isect_label, mc)
        
        bits = platform.architecture()[0]
        code = """
            #DATA
        """
        code += Ray.asm_struct()
        code += Triangle.asm_struct()
        code += HitPoint.asm_struct()
        code += " #CODE \n"
        code += " global " + label + ":\n" + """
        macro eq128 xmm3 = eax.Ray.origin
        macro eq128 xmm4 = eax.Ray.dir
        macro eq128 xmm5 = ebx.Triangle.v0
        macro eq128 xmm6 = ebx.Triangle.v1
        macro eq128 xmm7 = ebx.Triangle.v2
        macro push eax
        macro push ebx
        macro push ecx
        macro push edx
        """
        code += "call %s\n" % ray_isect_label
        code += """
        cmp eax, 0
        je _reject
        """
        if bits == '64bit':
            code += "mov rcx, qword [rsp + 8]\n"
        else:
            code += "mov ecx, dword [esp + 4]\n"
        code += """
        macro if xmm0 < ecx goto _accept
        _reject:
        """
        if bits == '64bit':
            code += "add rsp, 32\n"
        else:
            code += "add esp, 16\n"
        code += """
        xor eax, eax
        ret
        _accept:
        macro pop edx
        macro pop ecx
        macro pop ebx
        macro pop eax

        """
        if bits == '64bit':
            code += """
                mov esi, dword [rbx + Triangle.has_normals]
                mov edi, dword [rbx + Triangle.has_uv]
            """
        else:
            code += """
                mov esi, dword [ebx + Triangle.has_normals]
                mov edi, dword [ebx + Triangle.has_uv]
            """
        code += """
        macro generate_one xmm3
        macro eq32 xmm3 = xmm3 - xmm1 - xmm2
        cmp esi, 0
        jne _interpolate_normal
        macro eq128 xmm4 = ebx.Triangle.normal
        jmp _end_interpolation

        _interpolate_normal:
        """
        code += """
        macro broadcast xmm1 = xmm1[0]
        macro eq128 xmm4 = xmm1 * ebx.Triangle.n1
        macro broadcast xmm2 = xmm2[0]
        macro eq128 xmm5 = xmm2 * ebx.Triangle.n2
        macro broadcast xmm3 = xmm3[0]
        macro eq128 xmm6 = xmm3 * ebx.Triangle.n0
        macro eq128 xmm4 = xmm4 + xmm5 + xmm6
        macro normalization xmm4 {xmm6, xmm7}

        _end_interpolation:

        cmp edi, 0
        je _end_interpolate_uv
        macro eq32 xmm6 = xmm3 * ebx.Triangle.tu0
        macro eq32 xmm7 = xmm1 * ebx.Triangle.tu1
        macro eq32 xmm6 = xmm6 + xmm7
        macro eq32 xmm7 = xmm2 * ebx.Triangle.tu2
        macro eq32 edx.Hitpoint.u = xmm6 + xmm7 {xmm6}
        macro eq32 xmm6 = xmm3 * ebx.Triangle.tv0
        macro eq32 xmm7 = xmm1 * ebx.Triangle.tv1
        macro eq32 xmm6 = xmm6 + xmm7
        macro eq32 xmm7 = xmm2 * ebx.Triangle.tv2
        macro eq32 edx.Hitpoint.v = xmm6 + xmm7 {xmm6}

        _end_interpolate_uv:

        macro broadcast xmm0 = xmm0[0]
        macro eq128 xmm3 = eax.Ray.dir * xmm0 + eax.Ray.origin
        macro eq32 xmm5 = edx.Triangle.material_idx

        macro eq32 edx.Hitpoint.t = xmm0 {xmm3}
        macro eq32 edx.Hitpoint.material_idx = xmm5 {xmm5}
        macro eq128 edx.Hitpoint.hit = xmm3 {xmm3}
        macro eq128 edx.Hitpoint.normal = xmm4 {xmm4}
        mov eax, 1
        ret
        """
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangle_intersection" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    @classmethod
    def asm_struct_name(cls):
        return "Triangle"

    @classmethod
    def populate_ds(cls, ds, triangle, name):
        ds[name + ".v0"] = triangle.v0.to_ds() 
        ds[name + ".v1"] = triangle.v1.to_ds()
        ds[name + ".v2"] = triangle.v2.to_ds()
        if triangle.has_normals:
            ds[name + ".n0"] = triangle.n0.to_ds()
            ds[name + ".n1"] = triangle.n1.to_ds()
            ds[name + ".n2"] = triangle.n2.to_ds()
            ds[name + ".has_normals"] = 1
        else:
            ds[name + ".normal"] = triangle.normal.to_ds()
            ds[name + ".has_normals"] = 0

        if triangle.has_uv:
            ds[name + ".has_uv"] = 1
            ds[name + ".tu0"] = triangle.tu0
            ds[name + ".tu1"] = triangle.tu1
            ds[name + ".tu2"] = triangle.tu2
            ds[name + ".tv0"] = triangle.tv0
            ds[name + ".tv1"] = triangle.tv1
            ds[name + ".tv2"] = triangle.tv2
        else:
            ds[name + ".has_uv"] = 0


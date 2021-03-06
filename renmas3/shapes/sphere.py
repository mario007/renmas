import math

from ..base import Ray
from ..macros import create_assembler
from .hit import HitPoint
from .shape import Shape
from .bbox import BBox

class Sphere(Shape):
    __slots__ = ['origin', 'radius', 'material_idx']

    def __init__(self, origin, radius, material_idx=0):
        self.origin = origin
        self.radius = radius
        self.material_idx = material_idx

    def isect_b(self, ray, min_dist=99999.0): #ray direction must be normalized
        temp = ray.origin - self.origin
        a = ray.dir.dot(ray.dir)
        b = temp.dot(ray.dir) * 2.0
        c = temp.dot(temp) - self.radius * self.radius
        disc = b * b - 4.0 * a * c

        if disc < 0.0:
            return False
        else:
            e = math.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom #smaller root
            if t > 0.0005 and t < min_dist:
                return t
            
            t = (-b + e) / denom # larger root
            if t > 0.0005 and t < min_dist:
                return t
        return False

    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    # ecx = pointer to minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label):
        code = """
            #DATA
        """
        code += Ray.asm_struct() + cls.asm_struct() + """
        float two[4] = 2.0, 2.0, 2.0, 0.0
        float epsilon = 0.0005
        float minus_four = -4.0
        float zero = 0.0
        float one = 1.0
        float minus_one = -1.0
        #CODE
        """
        code += " global " + label + ":\n" + """
        macro eq128 xmm0 = eax.Ray.dir
        macro eq128 xmm1 = xmm0
        macro dot xmm0 = xmm0 * xmm0 {xmm6, xmm7}
        macro eq128 xmm2 = eax.Ray.origin - ebx.Sphere.origin 
        macro eq128 xmm3 = xmm2 * two
        macro dot  xmm3 = xmm3 * xmm1 {xmm6, xmm7}
        macro dot xmm2 = xmm2 * xmm2 {xmm6, xmm7}
        macro eq32 xmm4 = ebx.Sphere.radius
        macro eq32 xmm4 = xmm4 * xmm4
        macro eq32 xmm2 = xmm2 - xmm4

        ; a = xmm0, b = xmm3, c = xmm2, dir = xmm1

        macro eq32 xmm4 = xmm3 * xmm3
        macro eq32 xmm5 = xmm0 * xmm2 * minus_four
        macro eq32 xmm4 = xmm4 + xmm5
        macro if xmm4 < zero goto _reject
        macro sqrtss xmm5, xmm4
        macro eq32 xmm6 = xmm0 * two
        macro eq32 xmm7 = xmm3 * minus_one
        macro eq32 xmm7 = xmm7 - xmm5
        macro eq32 xmm7 = xmm7 / xmm6
        macro if xmm7 > epsilon goto _populate
        macro eq32 xmm7 = xmm5 - xmm3
        macro eq32 xmm7 = xmm7 / xmm6
        macro if xmm7 > epsilon goto _populate

        xor eax, eax 
        ret

        _populate:
        macro if xmm7 > ecx goto _reject 
        macro eq128 xmm0 = xmm7
        mov eax, 1
        ret

        _reject:
        xor eax, eax
        ret
        """

        assembler = create_assembler()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_sphere_b" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)


    def isect(self, ray, min_dist=999999.0): #ray direction must be normalized
        temp = ray.origin - self.origin
        a = ray.dir.dot(ray.dir)
        b = temp.dot(ray.dir) * 2.0
        c = temp.dot(temp) - self.radius * self.radius
        disc = b * b - 4.0 * a * c

        if disc < 0.0:
            return False
        else:
            e = math.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom #smaller root
            if t > 0.0005 and t < min_dist:
                normal = (temp + ray.dir * t) * ( 1.0 / self.radius)
                hit_point = ray.origin + ray.dir * t
                theta = math.acos(normal.y)
                phi = math.atan2(normal.x, normal.z)
                if phi < 0.0: phi += 2 * math.pi
                u = phi / (2 * math.pi) 
                v = 1 - theta / math.pi
                return HitPoint(t, hit_point, normal, self.material_idx, u, v)
            
            t = (-b + e) / denom # larger root
            if t > 0.0005 and t < min_dist:
                normal = (temp + ray.dir * t) * (1.0 / self.radius)
                hit_point = ray.origin + ray.dir * t
                theta = math.acos(normal.y)
                phi = math.atan2(normal.x, normal.z)
                if phi < 0.0: phi += 2 * math.pi
                u = phi / (2 * math.pi) 
                v = 1 - theta / math.pi
                return HitPoint(t, hit_point, normal, self.material_idx, u, v)
        return False

    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label):
        code = """
            #DATA
        """
        code += HitPoint.asm_struct() + Ray.asm_struct() + cls.asm_struct() + """
        float two[4] = 2.0, 2.0, 2.0, 0.0
        float epsilon = 0.0005
        float minus_four = -4.0
        float zero = 0.0
        float one = 1.0
        float minus_one = -1.0
        #CODE
        """
        code += " global " + label + ":\n" + """
        macro eq128 xmm0 = eax.Ray.dir
        macro eq128 xmm1 = xmm0
        macro dot xmm0 = xmm0 * xmm0 {xmm6, xmm7}
        macro eq128 xmm2 = eax.Ray.origin - ebx.Sphere.origin 
        macro eq128 xmm3 = xmm2 * two
        macro dot  xmm3 = xmm3 * xmm1 {xmm6, xmm7}
        macro dot xmm2 = xmm2 * xmm2 {xmm6, xmm7}
        macro eq32 xmm4 = ebx.Sphere.radius
        macro eq32 xmm4 = xmm4 * xmm4
        macro eq32 xmm2 = xmm2 - xmm4

        ; a = xmm0, b = xmm3, c = xmm2, dir = xmm1

        macro eq32 xmm4 = xmm3 * xmm3
        macro eq32 xmm5 = xmm0 * xmm2 * minus_four
        macro eq32 xmm4 = xmm4 + xmm5
        macro if xmm4 < zero goto _reject
        macro sqrtss xmm5, xmm4
        macro eq32 xmm6 = xmm0 * two
        macro eq32 xmm7 = xmm3 * minus_one
        macro eq32 xmm7 = xmm7 - xmm5
        macro eq32 xmm7 = xmm7 / xmm6
        macro if xmm7 > epsilon goto _populate
        macro eq32 xmm7 = xmm5 - xmm3
        macro eq32 xmm7 = xmm7 / xmm6
        macro if xmm7 > epsilon goto _populate

        xor eax, eax 
        ret

        _populate:
        macro if xmm7 > ecx goto _reject 

        macro broadcast xmm5 = xmm7[0]
        macro eq128 xmm6 = xmm5 * eax.Ray.dir
        macro eq128 xmm4 = eax.Ray.origin - ebx.Sphere.origin 
        macro eq128 xmm5 = xmm6 + eax.Ray.origin
        macro eq128 xmm3 = xmm6 + xmm4
        macro eq32 xmm2 = ebx.Sphere.radius
        macro broadcast xmm2 = xmm2[0]
        macro eq128 xmm3 = xmm3 / xmm2
        macro eq32 xmm1 = ebx.Sphere.material_idx

        macro eq32 edx.Hitpoint.t = xmm7 {xmm0}
        macro eq128 edx.Hitpoint.hit = xmm5 {xmm0}
        macro eq128 edx.Hitpoint.normal = xmm3 {xmm0}
        macro eq32 edx.Hitpoint.material_idx = xmm1 {xmm0}

        mov eax, 1
        ret

        _reject:
        xor eax, eax
        ret
        """
        
        assembler = create_assembler()
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_sphere" + str(id(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    def attributes(self):
        d = {}
        d["origin"] = self.origin.to_ds()
        d["radius"] = self.radius
        d["material_idx"] = self.material_idx
        return d

    @classmethod
    def asm_struct_name(cls):
        return "Sphere"

    @classmethod
    def asm_struct(cls):
        code = """
            struct Sphere
            float origin[4]
            float radius
            uint32 material_idx
            end struct
        """
        return code

    def bbox(self):

        epsilon = 0.001
        p0X = self.origin.x - self.radius - epsilon
        p0Y = self.origin.y - self.radius - epsilon
        p0Z = self.origin.z - self.radius - epsilon

        p1X = self.origin.x + self.radius + epsilon
        p1Y = self.origin.y + self.radius + epsilon
        p1Z = self.origin.z + self.radius + epsilon

        p0 = Vector3(p0X, p0Y, p0Z)
        p1 = Vector3(p1X, p1Y, p1Z)

        return BBox(p0, p1)

    def __str__(self):
        text = "Origin = " + str(self.origin) + " \n"
        text += "Radius = " + str(self.radius)
        return text 


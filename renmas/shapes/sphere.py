import math
import random
from .hitpoint import HitPoint
from .bbox import BBox
import renmas.utils as util
from renmas.maths import Vector3


class Sphere:
    def __init__(self, origin, radius, material):
        self.origin = origin
        self.radius = radius
        self.material = material

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
            if t > 0.00001 and t < min_dist:
                normal = (temp + ray.dir * t) * ( 1.0 / self.radius)
                hit_point = ray.origin + ray.dir * t
                return HitPoint(t, hit_point, normal, self.material, ray)
            
            t = (-b + e) / denom # larger root
            if t > 0.00001 and t < min_dist:
                normal = (temp + ray.dir * t) * (1.0 / self.radius)
                hit_point = ray.origin + ray.dir * t
                return HitPoint(t, hit_point, normal, self.material, ray)
        return False

    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    # TODO - maybe beacuse accept is rare dont't jump on reject - do it opositte jump on accept
    @classmethod
    def isect_asm(cls, runtime, label, populate=True):
        asm_structs = util.structs("ray", "sphere", "hitpoint")
        if util.AVX:
            line1 = " vsqrtss xmm5, xmm5, xmm5 \n"
        else:
            line1 = " sqrtss xmm5, xmm5 \n"

        ASM = """ 
        #DATA
        float epsilon = 0.00001
        float two = 2.0
        float minus_four = -4.0
        float zero = 0.0
        float one = 1.0
        float minus_one = -1.0
        """
        ASM += asm_structs + """
            ;eax = pointer to ray structure
            ;ebx = pointer to plane structure
            ;ecx = pointer to minimum distance
            ;edx = pointer to hitpoint
        #CODE
        """
        ASM += " global " + label + ":\n" + """
            macro eq128_128 xmm1 = eax.ray.dir, xmm2 = eax.ray.origin - ebx.sphere.origin
            macro dot xmm3 = xmm1 * xmm1 {xmm2}
            macro dot xmm4 = xmm2 * xmm1 {xmm3}
            macro eq32_32 xmm4 = xmm4 * two, xmm5 = ebx.sphere.radius * ebx.sphere.radius {xmm1, xmm2, xmm3, xmm4}
            macro dot xmm6 = xmm2 * xmm2 {xmm1, xmm3, xmm4, xmm5}
            macro eq32 xmm5 = xmm6 - xmm5 {xmm1, xmm2, xmm3, xmm4}
            macro eq32_32 xmm5 = xmm5 * xmm3, xmm6 = xmm4 * xmm4 {xmm1, xmm2, xmm3}
            macro eq32 xmm5 = xmm5 * minus_four {xmm1, xmm2, xmm3, xmm4, xmm6}
            macro eq32 xmm5 = xmm5 + xmm6 {xmm1, xmm2, xmm3, xmm4}
            
            ; temp = xmm2, a = xmm3 , b = xmm4, disc = xmm5, ray.dir = xmm1
            macro if xmm5 < zero goto _reject
        """
        ASM += line1 + """
            macro eq32 xmm3 = xmm3 * two {xmm1, xmm2, xmm4, xmm5}
            macro eq32_32 xmm3 = one / xmm3, xmm4 = xmm4 * minus_one {xmm1, xmm2, xmm5}
            macro eq32 xmm6 = xmm4 - xmm5 {xmm1, xmm2, xmm3, xmm5}
            macro eq32 xmm6 = xmm6 * xmm3 {xmm1, xmm2, xmm3, xmm4, xmm5}
            macro if xmm6 > epsilon goto populate_hitpoint
            macro eq32 xmm6 = xmm4 + xmm5 {xmm1, xmm2, xmm3}
            macro eq32 xmm6 = xmm6 * xmm3 {xmm1, xmm2, xmm3, xmm4, xmm5}
            macro if xmm6 > epsilon goto populate_hitpoint
            mov eax, 0
            ret

            populate_hitpoint:
            macro if xmm6 > ecx goto _reject 

            """

        if populate:
            ASM += """
            macro broadcast xmm5 = xmm6[0]
            macro eq128_32 xmm4 =  xmm5 * xmm1, xmm7 = ebx.sphere.radius {xmm2}
            macro eq32 edx.hitpoint.t = xmm6 {xmm2, xmm4, xmm7}
            macro eq128_128 edx.hitpoint.hit = xmm4 + eax.ray.origin, xmm5 = xmm2 + xmm4 {xmm7}
            macro broadcast xmm7 = xmm7[0] 
            macro eq128_32 edx.hitpoint.normal = xmm5 / xmm7, edx.hitpoint.mat_index = ebx.sphere.mat_index
            """

        ASM += """

            mov eax, 1
            ret

            _reject:
            mov eax, 0
            ret
        """
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_sphere_isect" + str(util.unique())
        runtime.load(name, mc)

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("sphere") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("sphere")

    def attributes(self):
        d = {}
        d["origin"] = (self.origin.x, self.origin.y, self.origin.z, 0.0)
        d["radius"] = self.radius
        if self.material is None:
            d["mat_index"] = 999999 #TODO solve this in better way 
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def name(cls):
        return "sphere"

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

        return BBox(p0, p1, None)


import math
import random
from .hitpoint import HitPoint
import renmas.utils as util
from renmas.maths import Vector3

class Sphere:
    def __init__(self, origin, radius, material):
        self.origin = origin
        self.radius = radius
        self.material = material

    def intersect(self, ray, min_dist=99999.0): #ray direction must be normalized
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

    @classmethod
    def intersectbool_asm(cls, runtime, label_name):
        asm_structs = util.structs("ray", "sphere", "hitpoint")
        if util.AVX:
            line1 = " vsqrtss xmm5, xmm5, xmm5 \n"
        else:
            line1 = " sqrtss xmm5, xmm5 \n"

        ASM = """ 
        #DATA
        float epsilon = 0.0001
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
        #CODE
        """
        ASM += " global " + label_name + ":\n" + """
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
            mov eax, 1
            ret

            _reject:
            mov eax, 0
            ret
        """
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        runtime.load("ray_sphere_intersection_bool", mc)

    @classmethod
    def intersect_asm(cls, runtime, label_name):
        asm_structs = util.structs("ray", "sphere", "hitpoint")
        if util.AVX:
            line1 = " vsqrtss xmm5, xmm5, xmm5 \n"
        else:
            line1 = " sqrtss xmm5, xmm5 \n"

        ASM = """ 
        #DATA
        float epsilon = 0.0001
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
        ASM += " global " + label_name + ":\n" + """
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
            macro broadcast xmm5 = xmm6[0]
            macro eq128_32 xmm4 =  xmm5 * xmm1, xmm7 = ebx.sphere.radius {xmm2}
            macro eq32 edx.hitpoint.t = xmm6 {xmm2, xmm4, xmm7}
            macro eq128_128 edx.hitpoint.hit = xmm4 + eax.ray.origin, xmm5 = xmm2 + xmm4 {xmm7}
            macro broadcast xmm7 = xmm7[0] 
            macro eq128_32 edx.hitpoint.normal = xmm5 / xmm7, edx.hitpoint.mat_index = ebx.sphere.mat_index

            mov eax, 1
            ret

            _reject:
            mov eax, 0
            ret
        """
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        runtime.load("ray_sphere_intersection_bool", mc)

    @classmethod
    def generate_asm(cls, runtime, label_name):
        # eax = pointer to ray structure
        # ebx = pointer to sphere structure
        # ecx = pointer to minimum distance
        # edx = pointer to hitpoint
        struct = AsmStructures()
        intersect = """
        #DATA 
        """
        intersect += struct.get_struct("sphere") + struct.get_struct("ray") + struct.get_struct("hitpoint") + """

        float two = 2.0
        float four = 4.0
        float epsilon = 0.0001
        float minus_one = -1.0

        #CODE 
        """
        intersect += "global " + label_name + ":" + """
        movaps xmm0, oword [eax + ray.origin]
        subps xmm0, oword [ebx + sphere.origin]  ;temp = ray.origin - self.origin
        movaps xmm1, oword [eax + ray.dir]
        movaps xmm2, xmm1
        dpps xmm1, xmm1, 0xf1   ;a = ray.dir.dot(ray.dir)
        movaps xmm3, xmm0 
        dpps xmm0, xmm2, 0xf1  ; b = temp.dot(ray.dir) * 2.0
        mulss xmm0, dword [two] 

        movaps xmm4, xmm3 
        dpps xmm3, xmm3, 0xf1   ;c = temp.dot(temp) - self.radius * self.radius
        movss xmm6, dword [ebx + sphere.radius]
        mulss xmm6, xmm6
        subss xmm3, xmm6 

        movss xmm7, dword [minus_one]
        mulss xmm7, xmm0  ; -b
        mulss xmm0, xmm0   ; disc = b * b - 4.0 * a * c
        movss xmm5, dword [four]
        mulss xmm5, xmm1
        mulss xmm5, xmm3
        subss xmm0, xmm5
        pxor xmm6, xmm6
        comiss xmm0, xmm6 ; if disc < 0 return False
        jc _false
        sqrtss xmm0, xmm0  ; e = sqrt(disc)
        mulss xmm1, dword [two] ; denom = 2.0 * a
        ;rcpss xmm2, xmm1   ; t = (-b -e) / denom #smaller root
        movaps xmm6, xmm7
        subss xmm6, xmm0
        ;mulss xmm6, xmm2
        divss xmm6, xmm1
        comiss xmm6, dword [epsilon]
        jnc  _true 
        movaps xmm6, xmm7
        addss xmm6, xmm0
        ;mulss xmm6, xmm2
        divss xmm6, xmm1
        comiss xmm6, dword [epsilon]
        jnc _true
        mov eax, 0
        ret

        _true: ; intersection ocur  
        comiss xmm6, dword [ecx] ; if t > min_dist don't populate structure 
        jnc _false    
        ;populate hitpoint structure
        movss xmm7, dword [ebx + sphere.radius]
        movaps xmm0, xmm6
        shufps xmm6, xmm6, 0x00            ;normal = (temp + ray.dir * t) * ( 1.0 / self.radius)
        mulps xmm6, oword [eax + ray.dir] ;hit_point = ray.origin + ray.dir * t
        addps xmm4, xmm6
        addps xmm6, oword [eax + ray.origin]
        movaps oword [edx + hitpoint.hit], xmm6
        movss dword [edx + hitpoint.t], xmm0
        shufps xmm7, xmm7, 0x00
        divps xmm4, xmm7
        movaps oword [edx + hitpoint.normal], xmm4
        mov esi, dword [ebx + sphere.mat_index]
        mov dword [edx + hitpoint.mat_index], esi
        mov eax, 1
        ret

        _false:
        mov eax, 0
        ret
        """
        asm = Tdasm()

        mc = asm.assemble(intersect, True)
        name = "sphere_intersect" 
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

    def struct_params(self):
        d = {}
        d["origin"] = (self.origin.x, self.origin.y, self.origin.z, 0.0)
        d["radius"] = self.radius
        if self.material is None:
            d["mat_index"] = 999999 #TODO try to solve this in better way 
        return d


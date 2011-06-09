
import renmas.utils as util
from .hitpoint import HitPoint

class Triangle:
    def __init__(self, v0, v1, v2, material):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        self.normal = (v1 - v0).cross(v2 - v0)
        self.normal.normalize()

    def isect(self, ray, min_dist = 999999.0):
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

        inv_denom = 1.0 / (a * m + b * q + c * s)

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

        return HitPoint(t, hit_point, self.normal, self.material, ray)

    def attributes(self):
        d = {}
        d["p0"] = (self.v0.x, self.v0.y, self.v0.z, 0.0)
        d["p1"] = (self.v1.x, self.v1.y, self.v1.z, 0.0)
        d["p2"] = (self.v2.x, self.v2.y, self.v2.z, 0.0)
        d["normal"] = (self.normal.x, self.normal.y, self.normal.z, 0.0)
        if self.material is None:
            d["mat_index"] = 999999 #TODO try to solve this in better way 
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def struct(cls):
        asm_code = """ #DATA
        """
        asm_code += util.structs("triangle") 
        asm_code += """
        #CODE
        #END
        """
        mc = util.get_asm().assemble(asm_code)
        return mc.get_struct("triangle")

    @classmethod
    def name(cls):
        return "triangle"


    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    # TODO - maybe beacuse accept is rare dont't jump on reject - do it opositte jump on accept
    @classmethod
    def isect_asm(cls, runtime, label, populate=True):
        asm_structs = util.structs("ray", "triangle", "hitpoint")

        ASM = """ 
        #DATA
        float epsilon = 0.0001
        float neg_epsilon = -0.0001
        float one = 1.0
        float zero = 0.0
        uint32 mask_abs[4] = 0x7FFFFFFF, 0, 0, 0
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
        macro eq128_128 xmm0 = ebx.triangle.p1 - ebx.triangle.p0, xmm1 = ebx.triangle.p2 - ebx.triangle.p0 
        ; e1 = xmm0 , e2 = xmm1
        macro eq128_128 xmm2 = eax.ray.dir, xmm3 = xmm1 {xmm0, xmm1}

        ; p = d x e2
        macro eq128_128 xmm4 = xmm2, xmm5 = xmm3 {xmm0, xmm1}
        """

        if util.AVX:
            ASM += """
                vshufps xmm2, xmm2, xmm2, 0xC9
                vshufps xmm3, xmm3, xmm3, 0xD2
                macro eq128 xmm2 = xmm2 * xmm3 {xmm0, xmm1}
                vshufps xmm4, xmm4, xmm4, 0xD2
                vshufps xmm5, xmm5, xmm5, 0xC9
            """
        else:
            ASM += """
                shufps xmm2, xmm2, 0xC9
                shufps xmm3, xmm3, 0xD2
                macro eq128 xmm2 = xmm2 * xmm3 {xmm0, xmm1}
                shufps xmm4, xmm4, 0xD2
                shufps xmm5, xmm5, 0xC9
            """
        ASM += """
            macro eq128 xmm4 = xmm4 * xmm5 {xmm0, xmm1, xmm2}
            macro eq128 xmm2 = xmm2 - xmm4 {xmm0, xmm1}

            macro dot xmm3 = xmm0 * xmm2 {xmm0, xmm1}
        """
        if util.AVX:
            ASM += "vpabsd xmm4, xmm3 \n"
        else:
            ASM += "movaps xmm4, oword [mask_abs] \n"
            ASM += "andps xmm4, xmm3 \n"

        ASM += """

            macro if xmm4 < epsilon goto reject
            macro eq32 xmm4 = one / xmm3 {xmm0, xmm1, xmm2, xmm3}

            ; f = xmm4
            macro eq128 xmm5 = eax.ray.origin - ebx.triangle.p0 {xmm0, xmm1, xmm2, xmm3, xmm4}
            ; s = xmm5

            macro dot xmm2 = xmm2 * xmm5 {xmm0, xmm1, xmm3, xmm4}
            ;s * p(s dot p) = xmm2
            macro eq32 xmm6 = xmm4 * xmm2 {xmm0, xmm1, xmm2, xmm3, xmm4, xmm5}

            macro if xmm6 < zero goto reject
            macro if xmm6 > one goto reject

            ; q = s x e1 
            macro eq128_128 xmm3 = xmm5, xmm7 = xmm0 
        """
        if util.AVX:
            ASM += """
                vshufps xmm5, xmm5, xmm5, 0xC9
                vshufps xmm0, xmm0, xmm0, 0xD2
                macro eq128 xmm0 = xmm0 * xmm5 

                vshufps xmm3, xmm3, xmm3, 0xD2
                vshufps xmm7, xmm7, xmm7, 0xC9
            """
        else:
            ASM += """
                shufps xmm5, xmm5, 0xC9
                shufps xmm0, xmm0, 0xD2
                macro eq128 xmm0 = xmm0 * xmm5 

                shufps xmm3, xmm3, 0xD2
                shufps xmm7, xmm7, 0xC9
            """

        ASM += """
            macro eq128 xmm3 = xmm3 * xmm7 
            macro eq128 xmm0 = xmm0 - xmm3

            macro dot xmm7 = xmm0 * eax.ray.dir {xmm1}
            macro eq32 xmm7 = xmm7 * xmm4

            macro if xmm7 < zero goto reject
            macro eq32 xmm7 = xmm7 + xmm6
            macro if xmm7 > one goto reject

            macro dot xmm6 = xmm1 * xmm0
            macro eq32 xmm6 = xmm6 * xmm4

            ;populate hitpoint structure
            ; t is in xmm6 , t can be negative so we eleminate those
            macro if xmm6 < zero goto reject
            macro if xmm6 > ecx goto reject
        """
        if populate:
            ASM += """
            macro eq32 edx.hitpoint.t = xmm6
            macro broadcast xmm7 = xmm6[0]
            macro eq128_32 edx.hitpoint.normal = ebx.triangle.normal, edx.hitpoint.mat_index = ebx.triangle.mat_index
            macro eq128 xmm5 = xmm7 * eax.ray.dir
            macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin
            """
        ASM += """

            mov eax, 1
            ret

            reject:
            mov eax, 0 
            ret


        """
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "ray_triangle_isect" + str(util.unique())
        runtime.load(name, mc)


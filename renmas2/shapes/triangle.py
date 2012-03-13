
import renmas2.switch as proc
from .hitpoint import HitPoint
from .bbox import BBox
from ..core import Vector3
from .shape import Shape

class Triangle(Shape):
    def __init__(self, v0, v1, v2, material=None, n0=None, n1=None, n2=None, u=None, v=None):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.material = material
        self.normal = None
        self.n0 = n0
        self.n1 = n1
        self.n2 = n2
        self.u = u
        self.v = v
        #TODO think -- raise exception if only one of three normals are passed to constructor
        if n0 is None:
            self.normal = (v1 - v0).cross(v2 - v0)
            self.normal.normalize()
            self.has_normals = False 
        else:
            self.n0.normalize()
            self.n1.normalize()
            self.n2.normalize()
            self.has_normals = True 

        if u is None:
            self.has_uv = False
        else:
            self.has_uv = True

    def isect_b(self, ray, min_dist=999999.0): #ray direction must be normalized
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
        return t

    # eax = pointer to ray structure
    # ebx = pointer to triangle structure
    # ecx = pointer to minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label, assembler, structures):
        code = """
            #DATA
        """
        code += structures.structs(('ray', 'triangle', 'hitpoint')) + """
        float epsilon= 0.00001
        float one = 1.0
        #CODE
        """
        if proc.AVX:
            code += " global " + label + ":\n" + """
            vmovaps xmm0, oword [ebx + triangle.v0]
            vsubps xmm1, xmm0, oword [ebx + triangle.v2]
            vsubps xmm3, xmm0, oword [eax + ray.origin]
            vmovaps xmm2, oword [eax + ray.dir]
            vsubps xmm0, xmm0, oword [ebx + triangle.v1]

            vmovlhps xmm4, xmm1, xmm3
            vpermilps xmm4, xmm4, 01110101B 
            vmovhlps xmm5, xmm2, xmm3
            vpermilps xmm5, xmm5, 00101010B 
            vmulps xmm7, xmm4, xmm5
            vmovlhps xmm6, xmm2, xmm3
            vpermilps xmm6, xmm6, 11010101B 
            vmovhlps xmm4, xmm1, xmm3
            vpermilps xmm4, xmm4, 10001010B 
            vmulps xmm4, xmm4, xmm6
            vsubps xmm7, xmm7, xmm4
            vmovlhps xmm5, xmm0, xmm3
            vpermilps xmm5, xmm5, 00001000B 
            vmulps xmm7, xmm7, xmm5
            vmovhlps xmm5, xmm0, xmm3
            vpermilps xmm5, xmm5, 10100010B 
            vmulps xmm6, xmm6, xmm5
            vmovlhps xmm4, xmm0, xmm3
            vpermilps xmm4, xmm4, 01011101B 
            vmovhlps xmm5, xmm2, xmm3
            vpermilps xmm5, xmm5, 00101010B 
            vmulps xmm5, xmm5, xmm4
            vsubps xmm6, xmm6, xmm5
            vmovlhps xmm5, xmm1, xmm3
            vpermilps xmm5, xmm5, 00100000B 
            vmulps xmm6, xmm6, xmm5
            vaddps xmm7, xmm7, xmm6
            vmovhlps xmm5, xmm1, xmm3
            vpermilps xmm5, xmm5, 10001010B 
            vmulps xmm4, xmm4, xmm5
            vmovlhps xmm6, xmm1, xmm3
            vpermilps xmm6, xmm6, 01110101B 
            vmovhlps xmm5, xmm0, xmm3
            vpermilps xmm5, xmm5, 10100010B 
            vmulps xmm6, xmm6, xmm5
            vsubps xmm4, xmm4, xmm6
            vmovlhps xmm5, xmm2, xmm3
            vpermilps xmm5, xmm5, 10000000B 
            vmulps xmm4, xmm4, xmm5
            vaddps xmm7, xmm7, xmm4
            vpermilps xmm3, xmm7, 00000000B 
            vdivps xmm7, xmm7, xmm3
            vpermilps xmm5, xmm7, 10101010B 
            vpermilps xmm4, xmm7, 01010101B 
            vpermilps xmm6, xmm7, 11111111B 

            ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta

            vpxor xmm3, xmm3, xmm3
            macro if xmm4 < xmm3 goto _reject
            macro if xmm5 < xmm3 goto _reject
            vaddss xmm4, xmm4, xmm5
            macro if xmm4 > one goto _reject

            vcomiss xmm6, dword [epsilon]
            jc _reject
            vcomiss xmm6, dword [ecx] ;minimum distance
            jnc _reject

            ;populate hitpoint structure
            ; t is in xmm6
            vmovaps xmm0, xmm6
            mov eax, 1
            ret

            _reject:
            xor eax, eax
            ret

            """

        else:
            code += " global " + label + ":\n" + """
            movaps xmm0, oword [ebx + triangle.v0]
            movaps xmm1, xmm0 
            movaps xmm3, xmm0
            subps xmm0, oword [ebx + triangle.v1]
            movaps xmm2, oword [eax + ray.dir]
            subps xmm1, oword [ebx + triangle.v2]
            subps xmm3, oword [eax + ray.origin]

            movaps xmm4, xmm1
            movlhps xmm4, xmm3
            shufps xmm4, xmm4, 01110101B
            movaps xmm5, xmm2
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 00101010B 
            movaps xmm7, xmm4
            mulps xmm7, xmm5
            movaps xmm6, xmm2
            movlhps xmm6, xmm3
            shufps xmm6, xmm6, 11010101B
            movaps xmm4, xmm1
            movhlps xmm4, xmm3
            shufps xmm4, xmm4, 10001010B
            mulps xmm4, xmm6
            subps xmm7, xmm4
            movaps xmm5, xmm0
            movlhps xmm5, xmm3
            shufps xmm5, xmm5, 00001000B
            mulps xmm7, xmm5
            movaps xmm5, xmm0
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 10100010B
            mulps xmm6, xmm5
            movaps xmm4, xmm0
            movlhps xmm4, xmm3
            shufps xmm4, xmm4, 01011101B
            movaps xmm5, xmm2
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 00101010B 
            mulps xmm5, xmm4
            subps xmm6, xmm5
            movaps xmm5, xmm1
            movlhps xmm5, xmm3
            shufps xmm5, xmm5, 00100000B
            mulps xmm6, xmm5
            addps xmm7, xmm6
            movaps xmm5, xmm1
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 10001010B
            mulps xmm4, xmm5
            movaps xmm6, xmm1
            movlhps xmm6, xmm3
            shufps xmm6, xmm6, 01110101B
            movaps xmm5, xmm0
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 10100010B
            mulps xmm6, xmm5
            subps xmm4, xmm6
            movaps xmm5, xmm2
            movlhps xmm5, xmm3
            shufps xmm5, xmm5, 10000000B
            mulps xmm4, xmm5
            addps xmm7, xmm4
            macro broadcast xmm3 = xmm7[0]
            divps xmm7, xmm3
            movhlps xmm5, xmm7
            movaps xmm4, xmm7
            shufps xmm4, xmm4, 0x55 
            movaps xmm6, xmm7
            shufps xmm6, xmm6, 0xFF
            ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta

            pxor xmm3, xmm3
            macro if xmm4 < xmm3 goto _reject
            macro if xmm5 < xmm3 goto _reject
            addss xmm4, xmm5
            macro if xmm4 > one goto _reject

            comiss xmm6, dword [epsilon]
            jc _reject
            comiss xmm6, dword [ecx] ;minimum distance
            jnc _reject

            ;populate hitpoint structure
            ; t is in xmm6
            movaps xmm0, xmm6
            mov eax, 1
            ret

            _reject:
            xor eax, eax
            ret

            """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangle_intersection_bool" + str(hash(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    def isect(self, ray, min_dist=999999.0): #ray direction must be normalized

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

        return HitPoint(t, hit_point, self.normal, self.material, ray)

    # eax = pointer to ray structure
    # ebx = pointer to triangle structure
    # ecx = pointer to minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label, assembler, structures):

        code = """
            #DATA
        """
        code += structures.structs(('ray', 'triangle', 'hitpoint')) + """
        float epsilon= 0.00001
        float one = 1.0
        #CODE
        """
        if proc.AVX:
            code += " global " + label + ":\n" + """
            vmovaps xmm0, oword [ebx + triangle.v0]
            vsubps xmm1, xmm0, oword [ebx + triangle.v2]
            vsubps xmm3, xmm0, oword [eax + ray.origin]
            vmovaps xmm2, oword [eax + ray.dir]
            vsubps xmm0, xmm0, oword [ebx + triangle.v1]

            ; f f h f
            vmovlhps xmm4, xmm1, xmm3
            vpermilps xmm4, xmm4, 01110101B 

            ; k k k l
            vmovhlps xmm5, xmm2, xmm3
            vpermilps xmm5, xmm5, 00101010B 

            ; f f h f * k k k l
            vmulps xmm7, xmm4, xmm5

            ; g g g h
            vmovlhps xmm6, xmm2, xmm3
            vpermilps xmm6, xmm6, 11010101B 

            ; j j l j
            vmovhlps xmm4, xmm1, xmm3
            vpermilps xmm4, xmm4, 10001010B 

            ; g g g h * j j l j
            vmulps xmm4, xmm4, xmm6

            ; f f h f * k k k l - g g g h * j j l j
            vsubps xmm7, xmm7, xmm4

            ; a d a a
            vmovlhps xmm5, xmm0, xmm3
            vpermilps xmm5, xmm5, 00001000B 

            ; a d a a * (f f h f * k k k l - g g g h * j j l j)
            vmulps xmm7, xmm7, xmm5

            ; i l i i
            vmovhlps xmm5, xmm0, xmm3
            vpermilps xmm5, xmm5, 10100010B 

            ; g g g h * i l i i
            vmulps xmm6, xmm6, xmm5

            ; e h e e
            vmovlhps xmm4, xmm0, xmm3
            vpermilps xmm4, xmm4, 01011101B 

            ; k k k l
            vmovhlps xmm5, xmm2, xmm3
            vpermilps xmm5, xmm5, 00101010B 

            ; e h e e * k k k l
            vmulps xmm5, xmm5, xmm4

            ; g g g h * i l i i - e h e e * k k k l
            vsubps xmm6, xmm6, xmm5

            ; b b d b
            vmovlhps xmm5, xmm1, xmm3
            vpermilps xmm5, xmm5, 00100000B 

            ; b b d b * (g g g h * i l i i - e h e e * k k k l)
            vmulps xmm6, xmm6, xmm5

            vaddps xmm7, xmm7, xmm6

            ; j j l j
            vmovhlps xmm5, xmm1, xmm3
            vpermilps xmm5, xmm5, 10001010B 

            ; e e h e * j j l j 
            vmulps xmm4, xmm4, xmm5

            ; f f h f
            vmovlhps xmm6, xmm1, xmm3
            vpermilps xmm6, xmm6, 01110101B 

            ; i l i i
            vmovhlps xmm5, xmm0, xmm3
            vpermilps xmm5, xmm5, 10100010B 

            ; f f h f * i l i i
            vmulps xmm6, xmm6, xmm5

            ; e h e e * j j l j - f f h f * i l i i
            vsubps xmm4, xmm4, xmm6

            ; c c c d
            vmovlhps xmm5, xmm2, xmm3
            vpermilps xmm5, xmm5, 10000000B 

            ; c c c d * (e h e e * j j l j - f f h f * i l i i)
            vmulps xmm4, xmm4, xmm5

            vaddps xmm7, xmm7, xmm4

            vpermilps xmm3, xmm7, 00000000B 
            vdivps xmm7, xmm7, xmm3

            vpermilps xmm5, xmm7, 10101010B 
            vpermilps xmm4, xmm7, 01010101B 
            vpermilps xmm6, xmm7, 11111111B 

            ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta

            vpxor xmm3, xmm3, xmm3
            macro if xmm4 < xmm3 goto _reject
            macro if xmm5 < xmm3 goto _reject
            vaddss xmm4, xmm4, xmm5
            macro if xmm4 > one goto _reject

            vcomiss xmm6, dword [epsilon]
            jc _reject
            vcomiss xmm6, dword [ecx] ;minimum distance
            jnc _reject

            ;populate hitpoint structure
            ; t is in xmm6
            
            vmovaps xmm2, oword [eax + ray.dir]
            vmovaps xmm3, oword [ebx + triangle.normal]
            vmovss xmm4, dword [ebx + triangle.mat_index]

            vmovss dword [edx + hitpoint.t], xmm6 
            vmovaps oword [edx + hitpoint.normal], xmm3
            vmovss dword [edx + hitpoint.mat_index], xmm4
            macro broadcast xmm5 = xmm6[0]
            vmulps xmm5, xmm5, xmm2
            macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin {xmm0}

            mov eax, 1
            ret

            _reject:
            xor eax, eax
            ret

            """

        else:
            code += " global " + label + ":\n" + """
            movaps xmm0, oword [ebx + triangle.v0]
            movaps xmm1, xmm0 
            movaps xmm3, xmm0
            subps xmm0, oword [ebx + triangle.v1]
            movaps xmm2, oword [eax + ray.dir]
            subps xmm1, oword [ebx + triangle.v2]
            subps xmm3, oword [eax + ray.origin]

            ; f f h f
            movaps xmm4, xmm1
            movlhps xmm4, xmm3
            shufps xmm4, xmm4, 01110101B

            ; k k k l
            movaps xmm5, xmm2
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 00101010B 

            ; f f h f * k k k l
            movaps xmm7, xmm4
            mulps xmm7, xmm5

            ; g g g h
            movaps xmm6, xmm2
            movlhps xmm6, xmm3
            shufps xmm6, xmm6, 11010101B

            ; j j l j
            movaps xmm4, xmm1
            movhlps xmm4, xmm3
            shufps xmm4, xmm4, 10001010B

            ; g g g h * j j l j
            mulps xmm4, xmm6

            ; f f h f * k k k l - g g g h * j j l j
            subps xmm7, xmm4

            ; a d a a
            movaps xmm5, xmm0
            movlhps xmm5, xmm3
            shufps xmm5, xmm5, 00001000B

            ; a d a a * (f f h f * k k k l - g g g h * j j l j)
            mulps xmm7, xmm5

            ; i l i i
            movaps xmm5, xmm0
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 10100010B

            ; g g g h * i l i i
            mulps xmm6, xmm5

            ; e h e e
            movaps xmm4, xmm0
            movlhps xmm4, xmm3
            shufps xmm4, xmm4, 01011101B

            ; k k k l
            movaps xmm5, xmm2
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 00101010B 

            ; e h e e * k k k l
            mulps xmm5, xmm4

            ; g g g h * i l i i - e h e e * k k k l
            subps xmm6, xmm5

            ; b b d b
            movaps xmm5, xmm1
            movlhps xmm5, xmm3
            shufps xmm5, xmm5, 00100000B

            ; b b d b * (g g g h * i l i i - e h e e * k k k l)
            mulps xmm6, xmm5

            addps xmm7, xmm6

            ; j j l j
            movaps xmm5, xmm1
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 10001010B

            ; e e h e * j j l j 
            mulps xmm4, xmm5

            ; f f h f
            movaps xmm6, xmm1
            movlhps xmm6, xmm3
            shufps xmm6, xmm6, 01110101B

            ; i l i i
            movaps xmm5, xmm0
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 10100010B

            ; f f h f * i l i i
            mulps xmm6, xmm5

            ; e h e e * j j l j - f f h f * i l i i
            subps xmm4, xmm6

            ; c c c d
            movaps xmm5, xmm2
            movlhps xmm5, xmm3
            shufps xmm5, xmm5, 10000000B

            ; c c c d * (e h e e * j j l j - f f h f * i l i i)
            mulps xmm4, xmm5

            addps xmm7, xmm4

            macro broadcast xmm3 = xmm7[0]
            divps xmm7, xmm3

            movhlps xmm5, xmm7
            
            movaps xmm4, xmm7
            shufps xmm4, xmm4, 0x55 
            
            movaps xmm6, xmm7
            shufps xmm6, xmm6, 0xFF

            ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta
            
            pxor xmm3, xmm3
            macro if xmm4 < xmm3 goto _reject
            macro if xmm5 < xmm3 goto _reject
            addss xmm4, xmm5
            macro if xmm4 > one goto _reject

            comiss xmm6, dword [epsilon]
            jc _reject
            comiss xmm6, dword [ecx] ;minimum distance
            jnc _reject

            ;populate hitpoint structure
            ; t is in xmm6
            
            movaps xmm2, oword [eax + ray.dir]
            movaps xmm3, oword [ebx + triangle.normal]
            movss xmm4, dword [ebx + triangle.mat_index]

            movss dword [edx + hitpoint.t], xmm6 
            movaps oword [edx + hitpoint.normal], xmm3
            movss dword [edx + hitpoint.mat_index], xmm4
            macro broadcast xmm5 = xmm6[0]
            mulps xmm5, xmm2

            macro eq128 edx.hitpoint.hit = xmm5 + eax.ray.origin {xmm0}

            mov eax, 1
            ret

            _reject:
            xor eax, eax
            ret

            """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        name = "ray_triangle_intersection" + str(hash(cls))
        for r in runtimes:
            if not r.global_exists(label):
                r.load(name, mc)

    def attributes(self):
        d = {}
        d["v0"] = (self.v0.x, self.v0.y, self.v0.z, 0.0)
        d["v1"] = (self.v1.x, self.v1.y, self.v1.z, 0.0)
        d["v2"] = (self.v2.x, self.v2.y, self.v2.z, 0.0)
        d["normal"] = (self.normal.x, self.normal.y, self.normal.z, 0.0)
        if self.material is None:
            d["mat_index"] = 999999 #TODO try to solve this in better way 
        else:
            d["mat_index"] = self.material
        return d

    @classmethod
    def name(cls):
        return "triangle"

    def bbox(self):
        epsilon = 0.0001
        v0 = self.v0 
        v1 = self.v1
        v2 = self.v2
        minx = min(min(v0.x, v1.x), v2.x) - epsilon
        maxx = max(max(v0.x, v1.x), v2.x) + epsilon
        miny = min(min(v0.y, v1.y), v2.y) - epsilon
        maxy = max(max(v0.y, v1.y), v2.y) + epsilon
        minz = min(min(v0.z, v1.z), v2.z) - epsilon
        maxz = max(max(v0.z, v1.z), v2.z) + epsilon
        p0 = Vector3(minx, miny, minz)
        p1 = Vector3(maxx, maxy, maxz)
        return BBox(p0, p1, None)


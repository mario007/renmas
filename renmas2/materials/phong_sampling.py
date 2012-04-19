
import math
from random import random
from ..core import Vector3
from .sampling import Sampling
import renmas2.switch as proc

class PhongSampling(Sampling):
    def __init__(self, n):
        self.invpi = 1.0 / math.pi
        self._n = float(n)
        self._n1 = 2.0 / (self._n + 1.0)
        self._n2 = 1.0 / (self._n + 1.0)

    def _set_n(self, value):
        self._n = float(value)
        self._n1 = 2.0 / (self._n + 1.0)
        self._n2 = 1.0 / (self._n + 1.0)
    def _get_n(self):
        return self._n
    n = property(_get_n, _set_n)

    def next_direction(self, hitpoint):
        r1 = random()
        r2 = random()

        phi = 2.0 * math.pi * r2
        pu = math.sqrt(1.0 - math.pow(r1, self._n1)) * math.cos(phi)
        pv = math.sqrt(1.0 - math.pow(r1, self._n1)) * math.sin(phi)
        pw = math.pow(r1, self._n2)


        ndotwo = hitpoint.normal.dot(hitpoint.wo)
        r = hitpoint.normal * ndotwo * 2.0 - hitpoint.wo

        w = r
        tv = Vector3(0.0034, 1.0, 0.0071)
        u = tv.cross(w)
        u.normalize()
        v = u.cross(w)

        ndir = u * pu + v * pv + w * pw 
        ndir.normalize()
        if hitpoint.normal.dot(ndir) < 0.0:
            ndir = u * (-pu) + v * (-pv) + w * pw
            ndir.normalize()
        
        ndotwi = hitpoint.normal.dot(ndir)

        hitpoint.wi = ndir
        hitpoint.ndotwi = ndotwi

    def next_direction_asm(self, runtimes, structures, assembler):

        if proc.AVX:
            line1 = "vmovss xmm1, dword [ecx + 4*ebx] \n"
        else:
            line1 = "movss xmm1, dword [ecx + 4*ebx] \n"

        code = """ 
        #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            float pi[4] = 3.14159265359, 3.14159265359, 3.14159265359, 3.14159265359
            float one[4] = 1.0, 1.0, 1.0, 1.0
            float two[4] = 2.0, 2.0, 2.0, 2.0
            float tvector[4] = 0.0034, 1.0, 0.0071, 0.0
            float minus_one[4] = -1.0, -1.0, -1.0, 0.0

            float pu[4]
            float pv[4]
            float pw[4]
            float temp_r[4]
            float _n1[4]
            float _n2[4]

            uint32 ptr_hp
            uint32 idx = 0

            #CODE
        """
        code += """
            mov dword [ptr_hp], eax
            sub dword [idx], 1
            js _calculate_samples
            _gen_direction:
            mov eax, dword [ptr_hp]
            macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo {xmm5, xmm6}
            macro broadcast xmm0 = xmm0[0]
            macro eq128 xmm1 = eax.hitpoint.normal * two * xmm0 - eax.hitpoint.wo

            macro eq128 xmm7 = xmm1
            macro eq128 xmm0 = tvector
            macro cross xmm0 x xmm1 {xmm2, xmm3}
            macro normalization xmm0 {xmm1, xmm2}
            macro eq128 xmm1 = xmm7
            macro eq128 xmm6 = xmm0
            macro cross xmm0 x xmm1 {xmm2, xmm3}
            macro eq128 xmm5 = xmm0
            mov ebx, dword [idx]
            mov ecx, pu
            ;u=xmm6 v=xmm5 w = xmm7
            ; in line we load pu, pv or pw

            """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm0 = xmm6 * xmm1
            mov ecx, pv
        """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm3 = xmm5 * xmm1
            mov ecx, pw
        """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm1 = xmm1 * xmm7

            macro eq128 xmm4 = xmm0 + xmm3 + xmm1
            macro normalization xmm4 {xmm5, xmm6}


            macro eq128 eax.hitpoint.wi = xmm4 {xmm5}  
            macro dot xmm2 = xmm4 * eax.hitpoint.normal {xmm5, xmm6}
            macro eq32 eax.hitpoint.ndotwi = xmm2 {xmm5}
            macro call zero xmm5
            macro if xmm2 > xmm5 goto _end_next_dir

            macro eq128 xmm0 = xmm0 * minus_one
            macro eq128 xmm3 = xmm3 * minus_one
            macro eq128 xmm0 = xmm0 + xmm3 + xmm1
            macro normalization xmm0 {xmm5, xmm6}
            macro eq128 eax.hitpoint.wi = xmm0 {xmm5}  
            macro dot xmm2 = xmm0 * eax.hitpoint.normal {xmm5, xmm6}
            macro eq32 eax.hitpoint.ndotwi = xmm2 {xmm5}

            _end_next_dir:
            ret

            _calculate_samples:
            macro call random 

            macro eq128 temp_r = xmm0 {xmm7}
            macro eq128 xmm1 = _n2
            macro call fast_pow_ps
            macro eq128 pw = xmm0 {xmm7}
            macro eq128 xmm0 = temp_r
            macro eq128 xmm1 = _n1
            macro call fast_pow_ps
            macro eq128 xmm1 = one - xmm0

        """
        if proc.AVX:
            code += "vsqrtps xmm1, xmm1 \n"
        else:
            code += "sqrtps xmm1, xmm1 \n"

        code += """
            macro eq128 pu = xmm1 {xmm0}
            macro eq128 pv = xmm1 {xmm0}

            macro call random 

            macro eq128 xmm0 = xmm0 * pi * two
            macro call fast_sincos_ps
            macro eq128 xmm6 = xmm6 * pu
            macro eq128 xmm0 = xmm0 * pv

            macro eq128 pu = xmm6  {xmm6}
            macro eq128 pv = xmm0  {xmm0}
            mov dword [idx], 3
            jmp _gen_direction 
        """

        self.nd_asm_name = name = "phong_sampling" + str(abs(hash(self)))
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        #print(code)
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))
        for ds in self._ds:
            ds["_n1"] = (self._n1, self._n1, self._n1, self._n1)
            ds["_n2"] = (self._n2, self._n2, self._n2, self._n2)

    def pdf(self, hitpoint):
        hp = hitpoint
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi
        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            pdf = ((self._n + 1.0) / (2.0 * math.pi)) * math.pow(rdotwo, self._n) 
            return pdf
        return 0.0

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self):
        sufix = "phong_sampling" + str(abs(hash(self)))

        ASM = ""
        ASM += "#DATA \n"
        ASM += "float n%s\n" % sufix
        ASM += "float c%s\n" % sufix
        ASM += "float two%s = 2.0\n" % sufix

        ASM += "#CODE \n"
        ASM += "macro eq32 xmm0 = two%s * eax.hitpoint.ndotwi\n" % sufix 
        ASM += "macro broadcast xmm0 = xmm0[0]\n"
        ASM += "macro eq128 xmm0 = xmm0 * eax.hitpoint.normal - eax.hitpoint.wi\n"
        ASM += "macro dot xmm0 = xmm0 * eax.hitpoint.wo {xmm6, xmm7}\n"

        ASM += "macro call zero xmm1\n"
        ASM += "macro if xmm0 > xmm1 goto accept%s\n" % sufix 
        ASM += "macro call zero xmm0\n"
        ASM += "jmp end%s\n" % sufix 

        ASM += "accept%s:\n" % sufix 
        ASM += "macro eq32 xmm1 = n%s\n" % sufix 
        ASM += "macro call fast_pow_ss\n"
        ASM += "macro eq32 xmm0 = xmm0 * c%s\n" % sufix 

        ASM += "end%s:\n" % sufix 

        return ASM

    def pdf_ds(self, ds):
        sufix = "phong_sampling" + str(abs(hash(self)))
        c = (self._n + 1.0) / (2.0 * math.pi)
        ds['c' + sufix] = (self._n + 1.0) / (2.0 * math.pi)
        ds['n' + sufix] = self._n




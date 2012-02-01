import math
from random import random
from ..core import Vector3
from .sampling import Sampling
import renmas2.switch as proc

class HemisphereCos(Sampling):
    def __init__(self, e=1):
        self.e = e
        self.ie = 1.0 / (e + 1.0)
        self.invpi = 1.0 / math.pi

    def next_direction(self, hitpoint):
        r1 = random()
        r2 = random()

        phi = 2.0 * math.pi * r1
        # savjet phar  - 1 - r2 mozemo samo sa r2 zamijeniti jer je r random izmedu 0 i 1 
        #cos_theta = math.pow(1.0 - r2, 1.0/(self.e + 1.0))
        cos_theta = math.pow(r2, self.ie)
        sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)
        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        pu = sin_theta * cos_phi 
        pv = sin_theta * sin_phi
        pw = cos_theta

        w = hitpoint.normal
        tv = Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)

        ndir = u * pu + v * pv + w * pw 
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
            float ie[4]
            float pi[4] = 3.14159265359, 3.14159265359, 3.14159265359, 3.14159265359
            float one[4] = 1.0, 1.0, 1.0, 1.0
            float two[4] = 2.0, 2.0, 2.0, 2.0
            float tvector[4] = 0.0034, 1.0, 0.0071, 0.0

            float pu[4]
            float pv[4]
            float pw[4]

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
            macro eq128 xmm1 = eax.hitpoint.normal {xmm1}
            macro eq128 xmm7 = xmm1
            macro eq128 xmm0 = tvector
            macro cross xmm0 x xmm1 {xmm2, xmm3}
            macro normalization xmm0 {xmm1, xmm2}
            macro eq128 xmm1 = xmm7
            macro eq128 xmm6 = xmm0
            macro cross xmm0 x xmm1 {xmm2, xmm3}
            mov ebx, dword [idx]
            mov ecx, pu
            ; in line we load pu, pv or pw

            """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm0 = xmm0 * xmm1
            mov ecx, pv
        """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm6 = xmm6 * xmm1
            macro eq128 xmm0 = xmm0 + xmm6
            mov ecx, pw
        """
        code += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm1 = xmm1 * xmm7
            macro eq128 xmm0 = xmm0 + xmm1
            macro normalization xmm0 {xmm1, xmm2}
            macro eq128 eax.hitpoint.wi = xmm0 {xmm0}  
            macro dot xmm0 = xmm0 * xmm7 {xmm3, xmm4}
            macro eq32 eax.hitpoint.ndotwi = xmm0 {xmm0}
            ret

            _calculate_samples:
            macro call random 

        """
        if self.e == 1:
            if proc.AVX:
                code += "vsqrtps xmm0, xmm0 \n"
            else:
                code += "sqrtps xmm0, xmm0 \n"
        else:
            code += "macro eq128 xmm1 = ie \n" 
            code += "macro call fast_pow_ps \n"

        code += """
            macro eq128 pw = xmm0 {xmm0}
            macro eq128 xmm0 = xmm0 * xmm0
            macro eq128 xmm1 = one - xmm0
            """
        if proc.AVX:
            code += "vsqrtps xmm0, xmm1 \n"
        else:
            code += "sqrtps xmm0, xmm1 \n"

        code += """
            macro eq128 pu = xmm0 {xmm0}
            macro eq128 pv = xmm0 {xmm0}

            macro call random 

            macro eq128 xmm0 = xmm0 * pi * two
            macro call fast_sincos_ps
            macro eq128 xmm0 = xmm0 * pv
            macro eq128 xmm6 = xmm6 * pu

            macro eq128 pv = xmm0  {xmm0}
            macro eq128 pu = xmm6  {xmm6}
            mov dword [idx], 3
            jmp _gen_direction 
        """

        self.nd_asm_name = name = "hemisphere_cos" + str(hash(self))
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        #print(code)
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))
        for ds in self._ds:
            ds["ie"] = (self.ie, self.ie, self.ie, self.ie)

    def pdf(self, hitpoint):
        pdf = hitpoint.ndotwi * self.invpi
        return pdf

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self):
        sufix = str(hash(self))
        ASM = ""
        ASM += "#DATA \n"
        ASM += "float invpi%s = 0.318309886184 \n" % sufix
        ASM += "#CODE \n"
        ASM += "macro eq32 xmm0 = eax.hitpoint.ndotwi * invpi%s \n" % sufix
        return ASM

    def pdf_ds(self, ds):
        pass



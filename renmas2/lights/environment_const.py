
import math
from random import random
from .light import EnvironmentLight
from ..core import Vector3
import renmas2.switch as proc


class ConstEnvironmentLight(EnvironmentLight):
    def __init__(self, spectrum):
        self._spectrum = spectrum
        self._ds = []

    def _set_spectrum(self, value):
        self._spectrum = value
        self._populate_ds()
    def _get_spectrum(self):
        return self._spectrum
    spectrum = property(_get_spectrum, _set_spectrum)

    def _populate_ds(self):
        for ds in self._ds:
            s = self._spectrum
            ds["l_spectrum.values"] = s.to_ds()

    #eax - pointer to hitpoint structure
    def L_asm(self, runtimes, visible_label, assembler, structures):

        if proc.AVX:
            line1 = "vmovss xmm1, dword [ecx + 4*ebx] \n"
        else:
            line1 = "movss xmm1, dword [ecx + 4*ebx] \n"

        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
        spectrum l_spectrum
        float pi[4] = 3.14159265359, 3.14159265359, 3.14159265359, 3.14159265359
        float one[4] = 1.0, 1.0, 1.0, 1.0
        float two[4] = 2.0, 2.0, 2.0, 2.0
        float tvector[4] = 0.0034, 1.0, 0.0071, 0.0

        float pu[4]
        float pv[4]
        float pw[4]
        float t[4] = 50000000.0, 50000000.0, 50000000.0, 0.0

        uint32 ptr_hp
        uint32 idx = 0

        #CODE

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
            macro dot xmm1 = xmm0 * xmm7 {xmm3, xmm4}
            ; wi - xmm0, ndotwi - xmm1
        
        mov eax, dword [ptr_hp]
        macro dot xmm2 = xmm0 * eax.hitpoint.normal {xmm6, xmm7}
        macro call zero xmm5
        macro if xmm2 < xmm5 goto reject  

        macro eq128 eax.hitpoint.wi = xmm0 {xmm0}
        macro eq32 eax.hitpoint.ndotwi = xmm1 {xmm1}
        ; test visibility of two points
        
        macro eq128 xmm0 = xmm0 * t + eax.hitpoint.hit
        macro eq128 xmm1 = eax.hitpoint.hit
        """
        code += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 1
        lea ecx, dword [eax + hitpoint.l_spectrum]
        mov ebx, l_spectrum
        macro eq32 xmm0 = pi / eax.hitpoint.ndotwi
        macro spectrum ecx = xmm0 * ebx
        ret

        reject:
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        ret

        _calculate_samples:
            macro call random 
            macro eq128 xmm1 = one - xmm0

        """
        if proc.AVX:
            code += "vsqrtps xmm0, xmm0 \n"
            code += "vsqrtps xmm1, xmm1 \n"
        else:
            code += "sqrtps xmm0, xmm0 \n"
            code += "sqrtps xmm1, xmm1 \n"

        code += """
            macro eq128 pw = xmm0 {xmm0}
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

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.l_asm_name = name = "environment_const_L" + str(hash(self))
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc)) 
        self._populate_ds()

    def L(self, hitpoint, renderer):
        # 1. check visibility
        # 2. populate light vector in hitpoint and spectrum of light

        # 1. generate wi direction
        # sampling hemisphere
        r1 = random()
        r2 = random()

        phi = 2.0 * math.pi * r2
        pu = math.sqrt(1.0 - r1) * math.cos(phi)
        pv = math.sqrt(1.0 - r1) * math.sin(phi)
        pw = math.sqrt(r1)

        w = hitpoint.normal
        tv = Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)

        wi = u * pu + v * pv + w * pw 
        wi.normalize()

        ndotwi = hitpoint.normal.dot(wi)
        pdf = ndotwi / math.pi 

        hitpoint.wi = wi 
        hitpoint.ndotwi = ndotwi

        if ndotwi < 0.0:
            hitpoint.visible = False
            return False

        t = 50000000.0 # huge t
        dist_point = hitpoint.hit_point + wi * t
        ret = renderer._intersector.visibility(dist_point, hitpoint.hit_point)
        if ret:
            hitpoint.l_spectrum = self._spectrum * (1.0 / pdf)
            hitpoint.visible = True
            return True
        else:
            hitpoint.visible = False
            return False

    def Le(self, direction): # return constant spectrum
        return self._spectrum

    # in xmm0 is direction of ray
    def Le_asm(self, runtimes, assembler, structures, label):
        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            spectrum ret_spectrum 
            #CODE
        """
        code += "global " + label + ":\n"
        code += """
            mov eax, ret_spectrum 
            ret
        """
        mc = assembler.assemble(code, True)
        name = "evironment_const" + str(abs(hash(self)))
        self._ds = []
        for r in runtimes:
            ds = r.load(name, mc)
            ds["ret_spectrum.values"] = self._spectrum.to_ds()
            self._ds.append(ds)

    def convert_spectrums(self, converter):
        self._spectrum = converter.convert_spectrum(self._spectrum, True)


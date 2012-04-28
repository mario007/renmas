
import math
from random import random
from .light import EnvironmentLight
from ..core import Vector3


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

        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
        float position[4]
        spectrum l_spectrum
        float zero = 0.0
        uint32 ptr_hp
        #CODE
        mov dword [ptr_hp], eax ; save pointer to hitpoint
        macro eq128 xmm0 = position - eax.hitpoint.hit 
        macro normalization xmm0 {xmm6, xmm7}
        macro dot xmm1 = xmm0 * eax.hitpoint.normal {xmm6, xmm7}
        macro if xmm1 < zero goto reject  

        macro eq128 eax.hitpoint.wi = xmm0 {xmm0}
        macro eq32 eax.hitpoint.ndotwi = xmm1 {xmm1}
        ; test visibility of two points
        macro eq128 xmm0 = position
        macro eq128 xmm1 = eax.hitpoint.hit
        """
        code += "call " + visible_label + "\n" + """
        cmp eax, 1
        jne reject
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 1
        lea ecx, dword [eax + hitpoint.l_spectrum]
        mov ebx, l_spectrum
        macro spectrum ecx = ebx
        ret

        reject:
        mov eax, dword [ptr_hp]
        mov dword [eax + hitpoint.visible], 0
        ret
        """

        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.l_asm_name = name = "pointlight_L" + str(hash(self))
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

        t = 5000000.0 # huge t
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

    def convert_spectrums(self, converter):
        self._spectrum = converter.convert_spectrum(self._spectrum, True)


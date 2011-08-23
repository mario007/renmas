
import renmas
import math

class SpecularBRDF:
    def __init__(self, r):
        self.r = float(r)
        self.spectrum = renmas.core.Spectrum(float(r), float(r), float(r))
        self.spectrum = self.spectrum * 2.0
        self.spectrum2 = renmas.core.Spectrum(0.0, 0.0, 0.0)

    def brdf(self, hitpoint):
        if hitpoint.specular:
            hitpoint.specular = False
            return self.spectrum * (1.0 / hitpoint.ndotwi)
        else:
            hitpoint.specular = False
            return self.spectrum2

    def brdf_asm(self, runtime):
        #eax pointer to hitpoint
        name = "specular" + str(hash(self))
        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "#CODE \n"
        ASM += "mov ebx, dword [eax + hitpoint.specular] \n"
        ASM += "cmp ebx, 14 \n" #0-no specular sample
        ASM += "je " + name + "spec_brdf\n"
        ASM += "pxor xmm0, xmm0 \n" # put 0.0 in xmm0
        ASM += "jmp " + name + "end_spec \n"
        ASM += name + "spec_brdf: \n"
        ASM += "macro eq32 xmm1 = eax.hitpoint.ndotwi \n" 
        ASM += "macro broadcast xmm1 = xmm1[0] \n"
        ASM += "macro eq128 xmm0 = " + name + "spectrum \n"
        ASM += "macro eq128 xmm0 = xmm0 / xmm1 \n"
        ASM += name + "end_spec: \n"
        ASM += "mov dword [eax + hitpoint.specular], 0 \n"

        return ASM


    def populate_ds(self, ds):
        s = self.spectrum
        name = "specular" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)



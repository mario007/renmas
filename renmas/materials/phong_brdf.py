import renmas
import math
import renmas.utils as util

class PhongBRDF:
    def __init__(self, spectrum, e, k=None):
        self.spectrum = spectrum
        self.e = e
        self.k = k

    def brdf(self, hitpoint):
        hp = hitpoint
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi

        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            phong = self.spectrum * math.pow(rdotwo, self.e)
            if self.k is None:
                return phong * (1 / hitpoint.ndotwi)
            else:
                return phong * self.k * ( 1 / hitpoint.ndotwi)
        return renmas.core.Spectrum(0.0, 0.0, 0.0)

    def brdf_asm(self, runtime):
        
        util.load_func(runtime, "fast_pow_ss")
        #eax pointer to hitpoint
        name = "phong" + str(hash(self))

        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "float " + name + "k[4] \n"
        ASM += "float " + name + "zero_spectrum[4] = 0.0, 0.0, 0.0, 0.0 \n"
        ASM += "float " + name + "e\n"
        ASM += "float " + name + "two = 2.0 \n"
        ASM += "uint32 " + name + "hp_ptr \n"
        ASM += "#CODE \n"
        ASM += "mov dword [" + name + "hp_ptr], eax \n"
        ASM += "macro eq32 xmm0 = " + name + "two * eax.hitpoint.ndotwi \n"
        ASM += "macro broadcast xmm0 = xmm0[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 * eax.hitpoint.normal\n"
        ASM += "macro eq128 xmm0 = xmm0 - eax.hitpoint.wi \n"
        ASM += "macro dot xmm0 = xmm0 * eax.hitpoint.wo \n"
        ASM += "macro if xmm0 > " + name + "zero_spectrum goto " + name + "accept \n"
        ASM += "macro eq128 xmm0 = " + name + "zero_spectrum \n"
        ASM += "jmp " + name + "end \n"

        ASM +=  name + "accept:\n"
        ASM += "macro eq32 xmm1 = " + name + "e\n"
        ASM += "call fast_pow_ss \n"
        ASM += "macro broadcast xmm0 = xmm0[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 *" + name + "spectrum \n"
        ASM += "macro eq32 xmm1 = eax.hitpoint.ndotwi \n"
        ASM += "macro broadcast xmm1 = xmm1[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 / xmm1 \n"
        if self.k is not None:
            ASM += "macro eq128 xmm0 = xmm0 * " + name + "k\n"

        ASM += name + "end: \n" 

        return ASM

    def populate_ds(self, ds):
        s = self.spectrum
        name = "phong" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)
        name = "phong" + str(hash(self)) + "e"
        ds[name] = self.e
        if self.k is not None:
            name = "phong" + str(hash(self)) + "k"
            ds[name] = (self.k, self.k, self.k, 0.0)


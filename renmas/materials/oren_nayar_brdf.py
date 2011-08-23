
import renmas
import math
import renmas.utils as util

class OrenNayarBRDF:
    def __init__(self, spectrum, alpha, k=None):
        A = 1.0 - ((0.5 * alpha * alpha) / (alpha * alpha + 0.33))
        B = 0.45 * alpha * alpha / (alpha * alpha + 0.09)
        self.A = A
        self.B = B
        self.k = k
        self.spectrum = spectrum * (1 / math.pi)

    def brdf(self, hitpoint):
        hp = hitpoint
        ndotwo = hp.wo.dot(hp.normal)
        angle1 = math.acos(ndotwo)
        angle2 = math.acos(hp.ndotwi)
        
        _alpha = max(angle1, angle2)
        _beta = min(angle1, angle2)
        
        t1 = hp.normal * ndotwo
        t2 = hp.normal * hp.ndotwi
        v1 = hp.wo - t1
        v2 = hp.wi - t2
        v1.normalize()
        v2.normalize()
        _gamma = v1.dot(v2)

        temp1 = self.B * max(0.0, _gamma) * math.sin(_alpha) * math.tan(_beta)
        temp1 = (temp1 + self.A) 
        if self.k is None:
            return self.spectrum * temp1  
        else:
            return self.spectrum * temp1 * self.k 

    def brdf_asm(self, runtime):
        
        #eax pointer to hitpoint
        name = "oren" + str(hash(self))

        util.load_func(runtime, "fast_acos_ps", "fast_sin_ss", "fast_tan_ss")

        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "float " + name + "k[4] \n"
        ASM += "float " + name + "zero[4] = 0.0, 0.0, 0.0, 0.0 \n"
        ASM += "float " + name + "A \n"
        ASM += "float " + name + "B \n"
        ASM += "float " + name + "alpha \n"
        ASM += "float " + name + "beta \n"
        ASM += "uint32 " + name + "hp_ptr \n"
        ASM += "#CODE \n"
        ASM += "mov dword [" + name + "hp_ptr], eax \n"
        ASM += "macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo \n"
        ASM += "macro eq32 xmm1 = eax.hitpoint.ndotwi \n"
        ASM += "movlhps xmm0, xmm1 \n"
        ASM += "call fast_acos_ps \n"
        ASM += "movhlps xmm1, xmm0 \n"
        ASM += "macro eq32 xmm2 = xmm0 \n"
        ASM += "macro eq32 xmm3 = xmm1 \n"
        ASM += "minss xmm0, xmm1 \n"  # _beta
        ASM += "maxss xmm2, xmm3 \n" # _alpha
        ASM += "macro eq32 " + name + "alpha = xmm2 \n"
        ASM += "call fast_tan_ss \n"
        ASM += "macro eq32 " + name + "beta = xmm0 \n"
        ASM += "macro eq32 xmm0 = " + name + "alpha \n" 
        ASM += "call fast_sin_ss \n"
        ASM += "macro eq32 xmm0 = xmm0 * " + name + "beta \n"
        ASM += "macro eq32 " + name + "alpha = xmm0 \n" # sin(alpha) * tan(beta)  
        ASM += "mov eax, dword [" + name + "hp_ptr]\n"
        ASM += "macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo \n"
        ASM += "macro broadcast xmm0 = xmm0[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 * eax.hitpoint.normal \n"
        ASM += "macro eq128 xmm1 = eax.hitpoint.wo \n"
        ASM += "macro eq128 xmm1 = xmm1 - xmm0 \n"
        ASM += util.normalization("xmm1", "xmm4", "xmm5") #v1
        ASM += "macro eq32 xmm2 = eax.hitpoint.ndotwi \n"
        ASM += "macro broadcast xmm2 = xmm2[0] \n"
        ASM += "macro eq128 xmm2 = xmm2 * eax.hitpoint.normal {xmm1} \n"
        ASM += "macro eq128 xmm3 = eax.hitpoint.wi \n"
        ASM += "macro eq128 xmm3 = xmm3 - xmm2 {xmm1} \n"
        ASM += util.normalization("xmm3", "xmm5", "xmm6") #v2
        ASM += "macro dot xmm3 = xmm3 * xmm1 \n"
        ASM += "maxss xmm3, dword [" + name + "zero] \n"
        ASM += "macro eq32 xmm3 = xmm3 * " + name + "alpha \n"
        ASM += "macro eq32 xmm3 = xmm3 * " + name + "B \n"
        ASM += "macro eq32 xmm3 = xmm3 + " + name + "A \n"
        ASM += "macro broadcast xmm0 = xmm3[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 * " + name + "spectrum \n"

        if self.k is not None:
            ASM += "macro eq128 xmm0 = xmm0 * " + name + "k\n"

        return ASM

    def populate_ds(self, ds):
        s = self.spectrum
        name = "oren" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)
        if self.k is not None:
            name = "oren" + str(hash(self)) + "k"
            ds[name] = (self.k, self.k, self.k, 0.0)
        name = "oren" + str(hash(self)) + "A"
        ds[name] = self.A
        name = "oren" + str(hash(self)) + "B"
        ds[name] = self.B


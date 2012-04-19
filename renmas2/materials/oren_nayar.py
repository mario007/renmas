
import math

from .brdf import BRDF
import renmas2.switch as proc

class OrenNayar(BRDF):
    def __init__(self, spectrum, roughness, k=1.0):
        alpha = float(roughness)
        self._A = 1.0 - ((0.5 * alpha * alpha) / (alpha * alpha + 0.33))
        self._B = 0.45 * alpha * alpha / (alpha * alpha + 0.09)
        self._k = float(k)
        self._roughness = float(roughness)
        self._spectrum = spectrum * (1 / math.pi)

    def _set_roughness(self, value):
        self._roughness = float(value)
        alpha = float(value)
        self._A = 1.0 - ((0.5 * alpha * alpha) / (alpha * alpha + 0.33))
        self._B = 0.45 * alpha * alpha / (alpha * alpha + 0.09)
    def _get_roughness(self):
        return self._roughness
    roughness = property(_get_roughness, _set_roughness)

    def _set_k(self, value):
        self._k = value
    def _get_k(self):
        return self._k
    k = property(_get_k, _set_k)

    def _set_spectrum(self, value):
        self._spectrum = value * ( 1 / math.pi)
    def _get_spectrum(self):
        return self._spectrum * math.pi
    spectrum = property(_get_spectrum, _set_spectrum)

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

        temp1 = self._B * max(0.0, _gamma) * math.sin(_alpha) * math.tan(_beta)
        temp1 = (temp1 + self._A) 
        if self.k is None:
            return self._spectrum * temp1  
        else:
            return self._spectrum * (temp1 * self._k) 

    # eax pointer to hitpoint
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, structures):
        sufix = "oren_nayar_" + str(abs(hash(self)))

        ASM = ""
        ASM += "#DATA \n"
        ASM += "float A%s\n" % sufix 
        ASM += "float B%s\n" % sufix 
        ASM += "float k%s\n" % sufix 
        ASM += "float alpha%s\n" % sufix 
        ASM += "float beta%s\n" % sufix 
        ASM += "uint32 hp_ptr%s\n" % sufix 
        ASM += "spectrum  spectrum%s \n" % sufix 
        ASM += "spectrum  ret_spectrum%s \n" % sufix 
        ASM += "#CODE \n"
        ASM += "mov dword [hp_ptr%s], eax \n" % sufix
        ASM += "macro dot xmm0 = eax.hitpoint.wo * eax.hitpoint.normal {xmm6, xmm7}\n"
        ASM += "macro eq32 xmm1 = eax.hitpoint.ndotwi \n"
        if proc.AVX:
            ASM += "vmovlhps xmm0, xmm0, xmm1 \n"
        else:
            ASM += "movlhps xmm0, xmm1 \n"
        ASM += "macro call fast_acos_ps \n"
        if proc.AVX:
            ASM += "vmovhlps xmm1, xmm1, xmm0 \n"
        else:
            ASM += "movhlps xmm1, xmm0 \n"
        ASM += "macro eq128 xmm2 = xmm0 \n"
        ASM += "macro eq128 xmm3 = xmm1 \n"
        ASM += "macro call maxss xmm2, xmm3 \n" #alpha
        ASM += "macro call minss xmm0, xmm1 \n" #beta
        ASM += "macro eq32 alpha%s = xmm2 {xmm7} \n" % sufix
        ASM += "macro call fast_tan_ss \n"
        ASM += "macro eq32 beta%s = xmm0 {xmm7} \n" % sufix
        ASM += "macro eq32 xmm0 = alpha%s \n" % sufix
        ASM += "macro call fast_sin_ss \n"
        ASM += "macro eq32 alpha%s = xmm0 {xmm7} \n" % sufix
        ASM += "mov eax, dword [hp_ptr%s] \n" % sufix
        ASM += "macro eq128 xmm0 = eax.hitpoint.normal \n"
        ASM += "macro dot xmm1 = eax.hitpoint.wo * xmm0 {xmm6, xmm7}\n"
        ASM += "macro broadcast xmm1 = xmm1[0]\n"
        ASM += "macro eq32 xmm2 = eax.hitpoint.ndotwi \n"
        ASM += "macro broadcast xmm2 = xmm2[0]\n"
        ASM += "macro eq128 xmm1 = xmm1 * xmm0 \n" #t1
        ASM += "macro eq128 xmm2 = xmm2 * xmm0 \n" #t2
        ASM += "macro eq128 xmm3 = eax.hitpoint.wo - xmm1 \n"
        ASM += "macro eq128 xmm4 = eax.hitpoint.wi - xmm2 \n"
        ASM += "macro normalization xmm3 {xmm6, xmm7} \n "
        ASM += "macro normalization xmm4 {xmm6, xmm7} \n "
        ASM += "macro call zero xmm5 \n"
        ASM += "macro dot xmm3 = xmm3 * xmm4 {xmm6, xmm7} \n" #gamma
        ASM += "macro call maxss xmm3, xmm5 \n"
        ASM += "macro eq32 xmm3 = xmm3 * B%s * alpha%s * beta%s + A%s \n" % (sufix, sufix, sufix, sufix)
        if self._k:
            ASM += "macro eq32 xmm3 = xmm3 * k%s \n" % sufix

        ASM += "mov eax, ret_spectrum%s \n" % sufix 
        ASM += "mov ecx, spectrum%s \n" % sufix 
        ASM += "macro spectrum eax = xmm3 * ecx \n"
        return ASM

    def populate_ds(self, ds):
        sufix = "oren_nayar_" + str(abs(hash(self)))
        ds["spectrum" + sufix + ".values"] = self._spectrum.to_ds()
        if self._k:
            ds["k" + sufix] = self._k
        ds["A" + sufix] = self._A
        ds["B" + sufix] = self._B

    def convert_spectrums(self, converter):
        spectrum = self._spectrum *  math.pi
        spectrum = converter.convert_spectrum(spectrum)
        spectrum = spectrum * ( 1 / math.pi)
        self._spectrum = spectrum


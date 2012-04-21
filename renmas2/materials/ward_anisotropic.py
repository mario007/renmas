
import math
from .brdf import BRDF
from ..core import Vector3

class WardAnisotropic(BRDF):
    def __init__(self, spectrum, alpha, beta,  k=1.0, sampling=None):

        self._spectrum = spectrum
        self._alpha = float(alpha)
        self._beta = float(beta)
        self._k = float(k)
        self._sampling = sampling

        if sampling is not None:
            if hasattr(sampling, 'alpha'):
                sampling.alpha = self._alpha
            if hasattr(sampling, 'beta'):
                sampling.beta = self._beta

    def _set_alpha(self, value):
        self._alpha = float(value)
        if self._sampling is not None:
            if hasattr(self._sampling, 'alpha'):
                self._sampling.alpha = self._alpha
    def _get_alpha(self):
        return self._alpha
    alpha = property(_get_alpha, _set_alpha)

    def _set_beta(self, value):
        self._beta = float(value)
        if self._sampling is not None:
            if hasattr(self._sampling, 'beta'):
                self._sampling.beta = self._beta
    def _get_beta(self):
        return self._beta
    beta = property(_get_beta, _set_beta)

    def _set_k(self, value):
        self._k = value
    def _get_k(self):
        return self._k
    k = property(_get_k, _set_k)

    def _set_spectrum(self, value):
        self._spectrum = value
    def _get_spectrum(self):
        return self._spectrum
    spectrum = property(_get_spectrum, _set_spectrum)

    def brdf(self, hp):

        h = hp.wo + hp.wi
        h.normalize()

        ax2 = 1.0 / self._alpha
        ay2 = 1.0 / self._beta

        const1 = 4.0 * math.pi * self._alpha * self._beta
        vdotn = hp.wo.dot(hp.normal)
        if vdotn < 0.0: return self._spectrum.zero_spectrum()

        ldotn = hp.wi.dot(hp.normal)

        denom = const1 * math.sqrt(vdotn * ldotn)

        w = hp.normal
        tv = Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)

        hx = h.dot(u) * ax2
        hy = h.dot(v) * ay2

        hdotn = h.dot(hp.normal)
        exponent = (hx*hx + hy*hy) / (hdotn*hdotn) 
        re = math.exp(-exponent)

        s = self._spectrum * ((re / denom) * self._k) 
        return s

    # eax pointer to hitpoint
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, structures):
        sufix = "ward" + str(abs(hash(self)))
        ASM = ""
        ASM += "#DATA \n"
        ASM += "float alpha%s\n" % sufix
        ASM += "float beta%s\n" % sufix
        ASM += "float k%s\n" % sufix 
        ASM += "float const1%s\n" % sufix 
        ASM += "float denom%s\n" % sufix 
        ASM += "float inv_alpha%s\n" % sufix 
        ASM += "float inv_beta%s\n" % sufix 
        ASM += "float minus_one%s = -1.0\n" % sufix 
        ASM += "float tvector%s[4] = 0.0034, 1.0, 0.0071, 0.0 \n" % sufix
        ASM += "spectrum  spectrum%s \n" % sufix 
        ASM += "spectrum  zero_spectrum%s \n" % sufix 
        ASM += "spectrum  ret_spectrum%s \n" % sufix 
        ASM += "#CODE \n"
        ASM += "macro eq128 xmm0 = eax.hitpoint.wo + eax.hitpoint.wi \n"
        ASM += "macro normalization xmm0 {xmm1, xmm2} \n"
        ASM += "macro dot xmm1 = eax.hitpoint.wo * eax.hitpoint.normal {xmm6, xmm7} \n"
        ASM += "macro call zero xmm2 \n"
        ASM += "macro if xmm1 > xmm2 goto calc_ward%s \n" % sufix
        ASM += "mov eax, zero_spectrum%s \n" % sufix
        ASM += "jmp end_ward%s \n" % sufix 
        ASM += "calc_ward%s: \n" % sufix 
        ASM += "macro dot xmm2 = eax.hitpoint.wi * eax.hitpoint.normal {xmm6, xmm7} \n"
        ASM += "macro eq32 xmm2 = xmm2 * xmm1 \n"
        ASM += "macro call sqrtss xmm2, xmm2 \n"
        ASM += "macro eq32 denom%s = xmm2 * const1%s {xmm7}\n" % (sufix, sufix)

        ASM += "macro eq128 xmm3 = eax.hitpoint.normal \n"
        ASM += "macro eq128 xmm4 = tvector%s \n" % sufix
        ASM += "macro cross xmm4 x xmm3 {xmm6, xmm7} \n "
        ASM += "macro normalization xmm4 {xmm6, xmm7} \n" # v - vector
        ASM += "macro eq128 xmm5 = xmm4 \n"
        ASM += "macro eq128 xmm3 = eax.hitpoint.normal \n"
        ASM += "macro cross xmm5 x xmm3 {xmm6, xmm7} \n " # u - vector

        ASM += "macro dot xmm2 = xmm0 * xmm5 {xmm6, xmm7} \n"
        ASM += "macro eq32 xmm2 = xmm2 * inv_alpha%s \n" % sufix
        ASM += "macro eq32 xmm2 = xmm2 * xmm2 \n"
        ASM += "macro dot xmm3 = xmm0 * xmm4  {xmm6, xmm7} \n"
        ASM += "macro eq32 xmm3 = xmm3 * inv_beta%s \n"  % sufix
        ASM += "macro eq32 xmm3 = xmm3 * xmm3 \n"
        ASM += "macro dot xmm1 = xmm0 * eax.hitpoint.normal {xmm6, xmm7} \n"
        ASM += "macro eq32 xmm1 = xmm1 * xmm1 \n"
        ASM += "macro eq32 xmm0 = xmm2 + xmm3 \n"
        ASM += "macro eq32 xmm0 = xmm0 / xmm1 * minus_one%s \n" % sufix
        ASM += "macro call fast_exp_ss \n"
        ASM += "macro eq32 xmm0 = xmm0 / denom%s * k%s \n" % (sufix, sufix)

        ASM += "mov eax, ret_spectrum%s \n" % sufix 
        ASM += "mov ecx, spectrum%s \n" % sufix 
        ASM += "macro spectrum eax = xmm0 * ecx \n"

        ASM += "end_ward%s:\n" % sufix 
        return ASM 

    def populate_ds(self, ds):
        sufix = "ward" + str(abs(hash(self)))
        ds["spectrum" + sufix + ".values"] = self._spectrum.to_ds()
        ds["zero_spectrum" + sufix + ".values"] = self._spectrum.zero_spectrum().to_ds()
        ds["k" + sufix] = self._k
        ds["alpha" + sufix] = self._alpha
        ds["beta" + sufix] = self._beta
        ds["inv_alpha" + sufix] = 1.0 / self._alpha
        ds["inv_beta" + sufix] = 1.0 / self._beta
        const1 = 4.0 * math.pi * self._alpha * self._beta
        ds["const1" + sufix] = const1

    def convert_spectrums(self, converter):
        spectrum = converter.convert_spectrum(self._spectrum)
        self._spectrum = spectrum


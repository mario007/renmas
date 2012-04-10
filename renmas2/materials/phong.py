
import math
from .brdf import BRDF

class Phong(BRDF):
    def __init__(self, spectrum, n, k=1.0):
        self._spectrum = spectrum
        self._n = float(n)
        self._k = float(k)

    def _set_n(self, value):
        self._n = float(value)
    def _get_n(self):
        return self._n
    n = property(_get_n, _set_n)

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
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi
        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            if self._k:
                s = (self._n + 2.0) / (2 * math.pi) * self._k
            else:
                s = (self._n + 2.0) / (2 * math.pi)

            phong = self._spectrum * (math.pow(rdotwo, self._n) * s)
            return phong

        return self._spectrum.zero_spectrum()

    # eax pointer to hitpoint
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, structures):

        name = "phong" + str(abs(hash(self)))

        ASM = ""
        ASM += "#DATA \n"
        ASM += "float %sn\n" % name
        ASM += "float %sk\n" % name
        ASM += "float %stwo=2.0\n" % name
        ASM += "spectrum  %sspectrum \n" % name 
        ASM += "spectrum  %szero_spectrum \n" % name 
        ASM += "spectrum  %sret_spectrum \n" % name 
        ASM += "#CODE \n"
        ASM += "macro eq32 xmm0 = %stwo * eax.hitpoint.ndotwi\n" % name
        ASM += "macro broadcast xmm0 = xmm0[0]\n"
        ASM += "macro eq128 xmm0 = xmm0 * eax.hitpoint.normal - eax.hitpoint.wi\n"
        ASM += "macro dot xmm0 = xmm0 * eax.hitpoint.wo {xmm6, xmm7}\n"

        ASM += "macro call zero xmm1\n"
        ASM += "macro if xmm0 > xmm1 goto %saccept\n" % name
        ASM += "mov eax, %szero_spectrum \n" %name
        ASM += "jmp %send\n" % name

        ASM += "%saccept:\n" % name
        ASM += "macro eq32 xmm1 = %sn\n" % name
        ASM += "macro call fast_pow_ss\n"
        ASM += "macro eq32 xmm0 = xmm0 * %sk\n" % name

        ASM += "mov eax, %sret_spectrum\n" % name
        ASM += "mov ecx, %sspectrum\n" % name

        ASM += "macro spectrum eax = xmm0 * ecx\n"
        ASM += "%send:\n" % name
        return ASM


    def populate_ds(self, ds):

        name = "phong" + str(abs(hash(self)))
        ds[name + "spectrum.values"] = self._spectrum.to_ds() 
        if self._k:
            s = (self._n + 2.0) / (2 * math.pi) * self._k
            ds[name + "k"] = s
        else:
            s = (self._n + 2.0) / (2 * math.pi)
            ds[name + "k"] = s
        ds[name + "n"] = self._n
        ds[name + "zero_spectrum.values"] = self._spectrum.zero_spectrum().to_ds()



    def convert_spectrums(self, converter):
        spectrum = converter.convert_spectrum(self._spectrum)
        self._spectrum = spectrum



import math
from .brdf import BRDF

class Phong(BRDF):
    def __init__(self, spectrum, n, k=None):
        self.spectrum = spectrum
        self.n = float(n)
        self.k = k

    def brdf(self, hp):
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi
        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            if self.k:
                s = (self.n + 2.0) / (2 * math.pi) * self.k
            else:
                s = (self.n + 2.0) / (2 * math.pi)

            phong = self.spectrum * (math.pow(rdotwo, self.n) * s)
            return phong

        return self.spectrum.zero_spectrum()

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
        ds[name + "spectrum.values"] = self.spectrum.to_ds() 
        if self.k:
            s = (self.n + 2.0) / (2 * math.pi) * self.k
            ds[name + "k"] = s
        else:
            s = (self.n + 2.0) / (2 * math.pi)
            ds[name + "k"] = s
        ds[name + "n"] = self.n
        ds[name + "zero_spectrum.values"] = self.spectrum.zero_spectrum().to_ds()



    def convert_spectrums(self, converter):
        spectrum = converter.convert_spectrum(self.spectrum)
        self.spectrum = spectrum


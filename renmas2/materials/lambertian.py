import math
from .brdf import BRDF

class Lambertian(BRDF):
    def __init__(self, spectrum, k=1.0):
        self._spectrum = spectrum * ( 1 / math.pi)
        self._k = float(k)

    def brdf(self, hp):
        if self._k:
            hp.f_spectrum = self._spectrum * self._k
        else:
            hp.f_spectrum = self._spectrum
        return hp.f_spectrum

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

    # eax pointer to hitpoint
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, structures):
        
        #eax pointer to hitpoint
        name = "lambertian" + str(hash(self))
        ASM = ""
        ASM += "#DATA \n"
        ASM += "spectrum  %sspectrum \n" % name 
        ASM += "#CODE \n"
        ASM += "mov eax, %sspectrum \n" %name
        return ASM

    def populate_ds(self, ds):
        if self._k:
            s = self._spectrum * self._k
        else:
            s = self._spectrum
        name = "lambertian" + str(hash(self)) + "spectrum.values"
        ds[name] = s.to_ds() 

    def convert_spectrums(self, converter):
        spectrum = self._spectrum *  math.pi
        spectrum = converter.convert_spectrum(spectrum)
        spectrum = spectrum * ( 1 / math.pi)
        self._spectrum = spectrum



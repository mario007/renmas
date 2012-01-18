import math
from .brdf import BRDF

class Lambertian(BRDF):
    def __init__(self, spectrum, k=None):
        self.spectrum = spectrum * ( 1 / math.pi)
        self.k = k

    def brdf(self, hp):
        if self.k:
            hp.f_spectrum = self.spectrum * self.k
        else:
            hp.f_spectrum = self.spectrum
        return hp.f_spectrum

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
        if self.k:
            s = self.spectrum * self.k
        else:
            s = self.spectrum
        name = "lambertian" + str(hash(self)) + "spectrum.values"
        ds[name] = s.to_ds() 

    def convert_spectrums(self, converter):
        spectrum = self.spectrum *  math.pi
        spectrum = converter.convert_spectrum(spectrum)
        spectrum = spectrum * ( 1 / math.pi)
        self.spectrum = spectrum



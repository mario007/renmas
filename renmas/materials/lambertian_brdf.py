import renmas
import math

class LambertianBRDF:
    def __init__(self, spectrum, k=None):
        self.spectrum = spectrum * ( 1 / math.pi)
        self.k = k

    def brdf(self, hitpoint):
        if self.k is None:
            return self.spectrum
        else:
            return self.spectrum * self.k

    def brdf_asm(self, runtime):
        
        #eax pointer to hitpoint
        name = "lamb" + str(hash(self))

        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "float " + name + "k[4] \n"
        ASM += "#CODE \n"
        ASM += "macro eq128 xmm0 = " + name + "spectrum \n"
        if self.k is not None:
            ASM += "macro eq128 xmm0 = xmm0 * " + name + "k\n"

        return ASM

    def populate_ds(self, ds):
        s = self.spectrum
        name = "lamb" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)
        if self.k is not None:
            name = "lamb" + str(hash(self)) + "k"
            ds[name] = (self.k, self.k, self.k, 0.0)


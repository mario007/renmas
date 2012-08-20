
import math
from .brdf import BRDF

class Lambertian(BRDF):
    def __init__(self, spectrum, k=1.0):
        self._spectrum = spectrum * ( 1 / math.pi)
        self._k = float(k)
        self._ds = None

    def brdf(self, sp):
        sp.f_spectrum = self._spectrum * self._k
        return sp.f_spectrum

    def _set_k(self, value):
        self._k = value
        self._populate_ds()
    def _get_k(self):
        return self._k
    k = property(_get_k, _set_k)

    def _set_spectrum(self, value):
        self._spectrum = value * ( 1 / math.pi)
        self._populate_ds()
    def _get_spectrum(self):
        return self._spectrum * math.pi
    spectrum = property(_get_spectrum, _set_spectrum)

    # eax pointer to shadepoint 
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, label):

        #eax pointer to shadepoint 
        code = " #DATA \n" + self._spectrum.struct() + """
        spectrum lamb_spectrum
        #CODE
        """
        code += 'global ' + label + ':\n' + """
        macro mov eax, lamb_spectrum
        ret
        """
        mc = assembler.assemble(code, True)
        name = 'lambertian' + str(id(self))
        self._ds = [r.load(name, mc) for r in runtimes]
        self._populate_ds()

    def _populate_ds(self):
        if self._ds is None:
            return
        for ds in self._ds:
            s = self._spectrum * self._k
            ds['lamb_spectrum.values'] = s.to_ds()

    def convert_spectrums(self, col_mgr):
        spectrum = self._spectrum *  math.pi
        spectrum = col_mgr.convert_spectrum(spectrum)
        spectrum = spectrum * ( 1 / math.pi)
        self._spectrum = spectrum
        self._ds = None


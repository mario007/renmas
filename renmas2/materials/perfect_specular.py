
from .brdf import BRDF

# Note here fresnel must be FresnelDielectric
class PerfectSpecular(BRDF):
    def __init__(self, spectrum, fresnel, k=1.0):

        self._spectrum = spectrum
        self._fresnel = fresnel
        self._k = k

    def _set_spectrum(self, value):
        self._spectrum = value
    def _get_spectrum(self):
        return self._spectrum
    spectrum = property(_get_spectrum, _set_spectrum)

    def _set_k(self, value):
        self._k = value
    def _get_k(self):
        return self._k
    k = property(_get_k, _set_k)

    def _set_ior(self, value):
        self._fresnel.ior = value
    def _get_ior(self):
        return self._fresnel.ior
    ior = property(_get_ior, _set_ior)

    def _get_simple_ior(self):
        return self._fresnel.approx_ior
    simple_ior = property(_get_simple_ior)

    def brdf(self, hp):

        if hp.specular == 89: # delta distribution

            ret = self._fresnel.evaluate(hp).mix_spectrum(self._spectrum) * (self._k/hp.ndotwi) 
            #ret = self._fresnel.evaluate(hp)
            return ret
        else:
            return self._spectrum.zero_spectrum()

    # eax pointer to hitpoint
    # in eax must return reflectance
    def brdf_asm(self, runtimes, assembler, structures):
        sufix = "perfect_specular" + str(abs(hash(self)))

        ASM = ""
        ASM += "#DATA \n"
        ASM += "float k%s\n" % sufix
        ASM += "spectrum  spectrum%s \n" % sufix 
        ASM += "spectrum  zero_spectrum%s \n" % sufix 
        ASM += "spectrum  ret_spectrum%s \n" % sufix 
        ASM += "uint32 hp_ptr%s \n" % sufix
        ASM += "#CODE \n"
        ASM += "mov dword [hp_ptr%s], eax \n" % sufix
        ASM += "mov ebx, dword [eax + hitpoint.specular] \n"
        ASM += "cmp ebx, 89 \n" # delta function
        ASM += "je calc_brdf%s \n" % sufix
        ASM += "mov eax, zero_spectrum%s \n" % sufix
        ASM += "jmp end%s\n" % sufix 
        ASM += "calc_brdf%s: \n" % sufix
        # fresnel -- fresnel return result in eax 
        ASM += self._fresnel.evaluate_asm()
        ASM += "mov ebx, ret_spectrum%s \n" % sufix
        ASM += "macro spectrum ebx = eax \n"
        ASM += "mov ecx, spectrum%s \n" % sufix
        ASM += "macro spectrum ebx = ebx * ecx \n"
        ASM += "mov ebx, dword [hp_ptr%s] \n" % sufix
        ASM += "macro eq32 xmm0 = k%s / ebx.hitpoint.ndotwi \n" % sufix
        ASM += "mov eax, ret_spectrum%s \n" % sufix
        ASM += "macro spectrum eax = xmm0 * eax \n"

        ASM += "end%s:\n" % sufix 
        return ASM

    def populate_ds(self, ds):
        sufix = "perfect_specular" + str(abs(hash(self)))
        ds["spectrum" + sufix + ".values"] = self._spectrum.to_ds() 
        ds["zero_spectrum" + sufix + ".values"] = self._spectrum.zero_spectrum().to_ds() 
        ds["k" + sufix] = self._k
        self._fresnel.populate_ds(ds)

    def convert_spectrums(self, converter):
        spectrum = converter.convert_spectrum(self._spectrum)
        self._spectrum = spectrum

        self._fresnel.convert_spectrums(converter)


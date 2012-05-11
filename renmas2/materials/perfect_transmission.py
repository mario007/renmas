
from .btdf import BTDF 

# Note here fresnel must be FresnelDielectric
class PerfectTransmission(BTDF):
    def __init__(self, spectrum, fresnel, k=1.0, sampling=None):
        self._spectrum = spectrum
        self._k = k
        self._fresnel = fresnel
        self._one_spectrum = self._spectrum.zero_spectrum().set(1.0)
        self._sampling = sampling

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
        if self._sampling is not None:
            self._sampling.eta_in = self._fresnel._avg_eta_in
    def _get_ior(self):
        return self._fresnel.ior
    ior = property(_get_ior, _set_ior)

    def _get_simple_ior(self):
        return self._fresnel.approx_ior
    simple_ior = property(_get_simple_ior)

    def btdf(self, hp):
        if hp.specular == 65: # delta distribution
            ret = self._one_spectrum - self._fresnel.evaluate(hp)
            if hp.fliped: # ray is inside object
                eta = self._fresnel._eta_out.div_spectrum(self._fresnel._eta_in)
            else:
                eta = self._fresnel._eta_in.div_spectrum(self._fresnel._eta_out)
            eta = eta.mix_spectrum(eta)
            ret = ret.mix_spectrum(eta).mix_spectrum(self._spectrum) * (self._k/hp.ndotwi)
            return ret
        else:
            return self._spectrum.zero_spectrum()

    def btdf_asm(self, runtimes, assembler, structures):
        sufix = "perfect_transmission" + str(abs(hash(self)))

        ASM = ""
        ASM += "#DATA \n"
        ASM += "float k%s\n" % sufix
        ASM += "spectrum  spectrum%s \n" % sufix 
        ASM += "spectrum  zero_spectrum%s \n" % sufix 
        ASM += "spectrum  ret_spectrum%s \n" % sufix 
        ASM += "spectrum  one_spectrum%s \n" % sufix 
        ASM += "spectrum  eta_out%s \n" % sufix
        ASM += "spectrum  eta_in%s \n" % sufix
        ASM += "spectrum  temp%s \n" % sufix
        ASM += "uint32 hp_ptr%s \n" % sufix
        ASM += "#CODE \n"
        ASM += "mov dword [hp_ptr%s], eax \n" % sufix
        ASM += "mov ebx, dword [eax + hitpoint.specular] \n"
        ASM += "cmp ebx, 65 \n" # delta function
        ASM += "je calc_brdf%s \n" % sufix
        ASM += "mov eax, zero_spectrum%s \n" % sufix
        ASM += "jmp end%s\n" % sufix 
        ASM += "calc_brdf%s: \n" % sufix
        # fresnel -- fresnel return result in eax 
        ASM += self._fresnel.evaluate_asm()
        ASM += "mov ebx, ret_spectrum%s \n" % sufix
        ASM += "mov ecx, one_spectrum%s \n" % sufix
        ASM += "macro spectrum ebx = ecx - eax \n"

        ASM += "mov ecx, spectrum%s \n" % sufix
        ASM += "macro spectrum ebx = ebx * ecx \n"

        ASM += "mov eax, dword [hp_ptr%s] \n" % sufix
        ASM += "mov edx, dword [eax + hitpoint.fliped] \n"
        ASM += "cmp edx, 1 \n"
        ASM += "je _inside%s \n" % sufix
        ASM += "mov ebx, eta_in%s \n" % sufix
        ASM += "mov ecx, eta_out%s \n" % sufix
        ASM += "jmp _end_eta%s \n" % sufix
        ASM += "_inside%s: \n" % sufix
        ASM += "mov ebx, eta_out%s \n" % sufix
        ASM += "mov ecx, eta_in%s \n" % sufix
        ASM += "_end_eta%s: \n" % sufix
        ASM += "mov eax, temp%s \n" % sufix
        ASM += "macro spectrum eax = ebx / ecx \n"
        ASM += "macro spectrum eax = eax * eax \n"

        ASM += "mov ebx, ret_spectrum%s \n" % sufix
        ASM += "macro spectrum ebx = ebx * eax \n"

        ASM += "mov ebx, dword [hp_ptr%s] \n" % sufix
        ASM += "macro eq32 xmm0 = k%s / ebx.hitpoint.ndotwi \n" % sufix
        ASM += "mov eax, ret_spectrum%s \n" % sufix
        ASM += "macro spectrum eax = xmm0 * eax \n"

        ASM += "end%s:\n" % sufix 
        return ASM

    def populate_ds(self, ds):
        sufix = "perfect_transmission" + str(abs(hash(self)))
        ds["spectrum" + sufix + ".values"] = self._spectrum.to_ds() 
        ds["zero_spectrum" + sufix + ".values"] = self._spectrum.zero_spectrum().to_ds() 
        ds["one_spectrum" + sufix + ".values"] = self._spectrum.zero_spectrum().set(1.0).to_ds() 
        ds["eta_in" + sufix + ".values"] = self._fresnel._eta_in.to_ds()
        ds["eta_out" + sufix + ".values"] = self._fresnel._eta_out.to_ds() 
        ds["k" + sufix] = self._k
        self._fresnel.populate_ds(ds)

    def convert_spectrums(self, converter):
        spectrum = converter.convert_spectrum(self._spectrum)
        self._spectrum = spectrum
        self._one_spectrum = converter.convert_spectrum(self._one_spectrum)

        self._fresnel.convert_spectrums(converter)


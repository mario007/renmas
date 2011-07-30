
import renmas.core
import math
import random
import renmas.utils as util

from .brdf_sampling import HemisphereCos

# in hitpoint.spectrum is light spectrum
def Lambertian(spectrum): #TODO include or dont include ndotwi - make an option
    def brdf(hitpoint):
        return spectrum.mix_spectrum(hitpoint.spectrum) * hitpoint.ndotwi  
    return brdf

def Phong(spectrum, e):
    def brdf(hitpoint):
        hp = hitpoint
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi

        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            phong = spectrum * math.pow(rdotwo, e)
            return phong.mix_spectrum(hp.spectrum) 
        return renmas.core.Spectrum(0.0, 0.0, 0.0)
    return brdf

def Oren_Nayar(spectrum, alpha):
    A = 1.0 - ((0.5 * alpha * alpha) / (alpha * alpha + 0.33))
    B = 0.45 * alpha * alpha / (alpha * alpha + 0.09)

    def brdf(hitpoint):
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
        _gamma = v1.dot(v2)

        temp1 = B * max(0.0, _gamma) * math.sin(_alpha) * math.tan(_beta)
        temp1 = (temp1 + A) * hp.ndotwi
        return spectrum.mix_spectrum(hp.spectrum) * temp1
    return brdf

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

class ConstantBRDF:
    def __init__(self, spectrum, k=None):
        self.spectrum = spectrum
        self.k = k

    def brdf(self, hitpoint):
        if self.k is None:
            return self.spectrum * 1.0
        else:
            return self.spectrum * self.k

    def brdf_asm(self, runtime):
        
        #eax pointer to hitpoint
        name = "const" + str(hash(self))

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
        name = "const" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)
        if self.k is not None:
            name = "const" + str(hash(self)) + "k"
            ds[name] = (self.k, self.k, self.k, 0.0)


class PhongBRDF:
    def __init__(self, spectrum, e, k=None):
        self.spectrum = spectrum
        self.e = e
        self.k = k

    def brdf(self, hitpoint):
        hp = hitpoint
        r = hp.normal * hp.ndotwi * 2.0 - hp.wi

        rdotwo = r.dot(hp.wo)
        if rdotwo > 0.0:
            phong = self.spectrum * math.pow(rdotwo, self.e)
            if self.k is None:
                return phong * (1 / hitpoint.ndotwi)
            else:
                return phong * self.k * ( 1 / hitpoint.ndotwi)
        return renmas.core.Spectrum(0.0, 0.0, 0.0)

    def brdf_asm(self, runtime):
        
        util.load_func(runtime, "fast_pow_ss")
        #eax pointer to hitpoint
        name = "phong" + str(hash(self))

        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "float " + name + "k[4] \n"
        ASM += "float " + name + "zero_spectrum[4] = 0.0, 0.0, 0.0, 0.0 \n"
        ASM += "float " + name + "e\n"
        ASM += "float " + name + "two = 2.0 \n"
        ASM += "uint32 " + name + "hp_ptr \n"
        ASM += "#CODE \n"
        ASM += "mov dword [" + name + "hp_ptr], eax \n"
        ASM += "macro eq32 xmm0 = " + name + "two * eax.hitpoint.ndotwi \n"
        ASM += "macro broadcast xmm0 = xmm0[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 * eax.hitpoint.normal\n"
        ASM += "macro eq128 xmm0 = xmm0 - eax.hitpoint.wi \n"
        ASM += "macro dot xmm0 = xmm0 * eax.hitpoint.wo \n"
        ASM += "macro if xmm0 > " + name + "zero_spectrum goto " + name + "accept \n"
        ASM += "macro eq128 xmm0 = " + name + "zero_spectrum \n"
        ASM += "jmp " + name + "end \n"

        ASM +=  name + "accept:\n"
        ASM += "macro eq32 xmm1 = " + name + "e\n"
        ASM += "call fast_pow_ss \n"
        ASM += "macro broadcast xmm0 = xmm0[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 *" + name + "spectrum \n"
        ASM += "macro eq32 xmm1 = eax.hitpoint.ndotwi \n"
        ASM += "macro broadcast xmm1 = xmm1[0] \n"
        ASM += "macro eq128 xmm0 = xmm0 / xmm1 \n"
        if self.k is not None:
            ASM += "macro eq128 xmm0 = xmm0 * " + name + "k\n"

        ASM += name + "end: \n" 

        return ASM

    def populate_ds(self, ds):
        s = self.spectrum
        name = "phong" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)
        name = "phong" + str(hash(self)) + "e"
        ds[name] = self.e
        if self.k is not None:
            name = "phong" + str(hash(self)) + "k"
            ds[name] = (self.k, self.k, self.k, 0.0)


class Material:
    def __init__(self):
        self.components = []
        self.ds = None
        self.func_ptr = None
        self.sampling_brdf_ptr = None
        self.sampling = None
        self.emiter = None
        self.le_ptr = None

    def add_emiter(self, emiter):
        self.emiter = emiter

    def add_sampling(self, sampling):
        if self.sampling is None:
            self.sampling = [sampling]
        else:
            self.sampling.append(sampling)

    def add_component(self, component):
        self.components.append(component)

    def le(self, hitpoint):
        if self.emiter is None:
            return renmas.core.Spectrum(0.0, 0.0, 0.0) 
        else:
            return self.emiter.Le(hitpoint)

    def brdf(self, hitpoint):
        spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0) 
        for c in self.components:
            spectrum = spectrum + c.brdf(hitpoint) 
        
        hitpoint.brdf = spectrum
        return spectrum 

    def next_direction(self, hitpoint):
        if self.sampling is None:
            raise ValueError("There must exist some sampling tehnique!!!")
            return
        else: # implement to choose if we have mulitple sampling
            self.sampling[0].get_sample(hitpoint)
            self.sampling[0].pdf(hitpoint)
            self.brdf(hitpoint)

    def next_direction_asm(self, runtime):

        self.sampling[0].get_sample_asm(runtime)

        f_ptr = self.sampling[0].func_ptr


        asm_structs = util.structs("hitpoint")
        #eax pointer to hitpoint
        ASM = """ 
        #DATA
        """
        ASM += asm_structs + """
        float zero = 0.0
        float pdf
        float inv_c
        uint32 sampling_ptr
        uint32 brdf_ptr
        uint32 hp_ptr
        #CODE
        mov dword [hp_ptr], eax ;save pointer to hitpoint
        ; call get sample 
        call dword [sampling_ptr]
        ; init pdf with zero - calculate pdf we can have multiple sampler
        mov eax, dword [zero]
        mov dword [pdf], eax

        mov eax, dword [hp_ptr]
        """
        for s in self.sampling:
            ASM += s.pdf_asm()
            ASM += """
                macro eq32 pdf = pdf + xmm0
                mov eax, dword [hp_ptr]
            """
        ASM += """
            macro eq32 xmm0 = pdf * inv_c 
            macro eq32 eax.hitpoint.pdf = xmm0
            call dword [brdf_ptr]
            ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "material_dir" + str(util.unique())

        ds = runtime.load(name, mc)
        ds["inv_c"] = 1.0 / len(self.sampling)
        ds["sampling_ptr"] = f_ptr
        ds["brdf_ptr"] = self.func_ptr

        self.sampling_brdf_ptr = runtime.address_module(name) 

    def le_asm(self, runtime):
        asm_structs = util.structs("hitpoint")
        #eax pointer to hitpoint
        ASM = """ 
        #DATA
        """
        ASM += asm_structs + """
        float zero_spectrum[4] = 0.0, 0.0, 0.0, 0.0
        #CODE
        """

        if self.emiter is None:
            ASM += "macro eq128 eax.hitpoint.le = zero_spectrum"
        else:
            raise ValueError("Its not implemented yet!! urgent implemtation is needed")

        ASM += """
        ret
        """
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "material_le" + str(util.unique())

        runtime.load(name, mc)
        self.le_ptr = runtime.address_module(name)

    def brdf_asm(self, runtime):

        asm_structs = util.structs("hitpoint")
        #eax pointer to hitpoint
        ASM = """ 
        #DATA
        """
        ASM += asm_structs + """
        float zero_spectrum[4] = 0.0, 0.0, 0.0, 0.0
        float spectrum[4] 
        uint32 hp_ptr

        #CODE
        mov dword [hp_ptr], eax ;save pointer to hitpoint
        macro eq128 spectrum = zero_spectrum
        """

        for c in self.components:
            ASM += c.brdf_asm(runtime)
            #in xmm0 is spectrum from component so we acumulate spectrum
            ASM += """
                macro eq128 spectrum = spectrum + xmm0
                mov eax, dword [hp_ptr]
            """
        ASM += """
        mov eax, dword [hp_ptr]
        macro eq128 eax.hitpoint.brdf = spectrum
        ret

        """

        #print(ASM)

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "material" + str(util.unique())

        self.ds = runtime.load(name, mc)
        self.func_ptr = runtime.address_module(name)

        for c in self.components:
            c.populate_ds(self.ds)

        self.next_direction_asm(runtime)


class OldMaterial:
    def __init__(self):
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def brdf(self, hitpoint):
        spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0) 
        for c in self.components:
            spectrum = spectrum + c(hitpoint)
        
        hitpoint.spectrum = spectrum


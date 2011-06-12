
import renmas.core
import math
import renmas.utils as util

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
    def __init__(self, spectrum):
        self.spectrum = spectrum

    def brdf(self, hitpoint):
        return self.spectrum.mix_spectrum(hitpoint.spectrum) * hitpoint.ndotwi  

    def brdf_asm(self):
        
        #eax pointer to hitpoint
        name = "lamb" + str(hash(self))

        ASM = """
        #DATA
        """
        ASM += "float " + name + "spectrum[4] \n" 
        ASM += "#CODE \n"
        ASM += "macro eq128 xmm0 = " + name + "spectrum * eax.hitpoint.spectrum\n"  
        ASM += "macro eq32 xmm1 = eax.hitpoint.ndotwi\n"
        ASM += "macro broadcast xmm1 = xmm1[0]\n"
        ASM += "macro eq128 xmm0 = xmm0 * xmm1\n"

        return ASM

    def populate_ds(self, ds):
        s = self.spectrum
        name = "lamb" + str(hash(self)) + "spectrum"
        ds[name] = (s.r, s.g, s.b, 0.0)

class Material:
    def __init__(self):
        self.components = []
        self.ds = None
        self.func_ptr = None

    def add_component(self, component):
        self.components.append(component)

    def brdf(self, hitpoint):
        spectrum = renmas.core.Spectrum(0.0, 0.0, 0.0) 
        for c in self.components:
            spectrum = spectrum + c.brdf(hitpoint)
        
        hitpoint.spectrum = spectrum
        return spectrum 

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
            ASM += c.brdf_asm()
            #in xmm0 is spectrum from component so we acumulate spectrum
            ASM += """
                macro eq128 spectrum = spectrum + xmm0
                mov eax, dword [hp_ptr]
            """
        ASM += """
        mov eax, dword [hp_ptr]
        macro eq128 eax.hitpoint.spectrum = spectrum
        ret

        """

        #print(ASM)

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "material" + str(util.unique())

        self.ds = runtime.load(name, mc)
        #FIXME - add method to runtime class so we can ask runtime for address of module
        self.func_ptr = runtime.modules[name][0]

        for c in self.components:
            c.populate_ds(self.ds)


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


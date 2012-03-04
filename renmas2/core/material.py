
from ..materials import BRDF, Sampling
from .spectrum import Spectrum

class Material:
    def __init__(self, spectrum):
        self._brdfs = []
        self._btdfs = []
        self._samplers = []
        self._emiter = None
        self._spectrum = spectrum

    def add(self, obj): #brdf or btdf or sampler 
        if isinstance(obj, BRDF):
            self._brdfs.append(obj)
        elif isinstance(obj, Sampling):
            self._samplers.append(obj)

        #TODO -- btdf sampler Log!!!

    def set_emiter(self, emiter):
        self._emiter = emiter

    def Le(self, hitpoint): #FIXME --- Tip:yes no in hitpoint
        raise ValueError("Not yet implemented")
        if self._emiter:
            raise ValueError("Not yet implemented")
        else:
            return Spectrum(False, (0.0, 0.0, 0.0))

    def next_direction(self, hitpoint):
        if len(self._samplers) == 0: raise ValueError("Missing sampler!!!")
        #TODO -- multiple samplers
        self._samplers[0].next_direction(hitpoint)
        pdf = 0.0
        for s in self._samplers:
            pdf += s.pdf(hitpoint)
        hitpoint.pdf = pdf / len(self._samplers)

    #eax pointer to hitpoint
    def next_direction_asm(self, runtimes, structures, assembler):
        if len(self._samplers) == 0: raise ValueError("Missing sampler!!!")
        #TODO -- multiple samplers
        self._samplers[0].next_direction_asm(runtimes, structures, assembler)

        ASM = """ 
        #DATA
        """
        ASM += structures.structs(("hitpoint",)) + """
        float zero = 0.0
        float pdf
        float inv_c
        uint32 sampling_ptr
        uint32 hp_ptr
        #CODE
        mov dword [hp_ptr], eax ;save pointer to hitpoint
        ; generate direction 
        call dword [sampling_ptr]

        ; init pdf with zero - calculate pdf multiple sampler supported
        mov eax, dword [zero]
        mov dword [pdf], eax

        mov eax, dword [hp_ptr]
        """
        for s in self._samplers:
            ASM += s.pdf_asm()
            ASM += """
                macro eq32 pdf = pdf + xmm0 {xmm1}
                mov eax, dword [hp_ptr]
            """
        ASM += """
            macro eq32 xmm0 = pdf * inv_c 
            macro eq32 eax.hitpoint.pdf = xmm0 {xmm0}
            ret
        """

        mc = assembler.assemble(ASM, True)
        #print(code)
        #mc.print_machine_code()
        self.nd_asm_name = name = "material_ndir" + str(hash(self))

        #TODO -- multiple samplers
        ndir_name = self._samplers[0].nd_asm_name
        for r in runtimes:
            ds = r.load(name, mc)
            ds["inv_c"] = 1.0 / len(self._samplers)
            ds["sampling_ptr"] = r.address_module(ndir_name)
            for s in self._samplers:
                s.pdf_ds(ds)

    def f(self, hp):
        spectrum = self._spectrum.zero_spectrum()
        for c in self._brdfs:
            spectrum = spectrum + c.brdf(hp) 
        
        #TODO -- set constraint that spectrum can be max 1.0 -- clamp
        hp.f_spectrum = spectrum
        hp.f_spectrum.clamp(0.0, 0.99)
        return spectrum 

    #eax pointer to hitpoint
    def f_asm(self, runtimes, assembler, structures):
        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            spectrum temp_spectrum 
            uint32 hp_ptr
            float low = 0.00
            float high = 0.99
            #CODE
            mov dword [hp_ptr], eax ;save pointer to hitpoint
            mov eax, temp_spectrum
            macro call zero xmm0
            macro spectrum eax = xmm0
            mov eax, dword [hp_ptr]
        """
        for c in self._brdfs:
            code += c.brdf_asm(runtimes, assembler, structures) #eax pointer to reflectance
            code += """
                mov ebx, temp_spectrum 
                macro spectrum ebx = ebx + eax
                mov eax, dword [hp_ptr]
            """
        code += """
        mov eax, temp_spectrum
        mov ebx, dword [hp_ptr]
        lea ecx, dword [ebx + hitpoint.f_spectrum]
        macro spectrum ecx = eax
        macro eq32 xmm0 = low
        macro eq32 xmm1 = high
        macro spectrum clamp ecx 
        ret

        """
        mc = assembler.assemble(code, True)
        #print(code)
        #mc.print_machine_code()
        self.f_asm_name = name = "material" + str(hash(self))
        self.ds = []
        for r in runtimes:
            self.ds.append(r.load(name, mc))

        for c in self._brdfs:
            for ds in self.ds:
                c.populate_ds(ds)

    def convert_spectrums(self, converter):
        self._spectrum = converter.convert_spectrum(self._spectrum)
        for c in self._brdfs:
            c.convert_spectrums(converter)


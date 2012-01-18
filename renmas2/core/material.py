
from ..materials import BRDF
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

        #TODO -- btdf sampler Log!!!

    def set_emiter(self, emiter):
        self._emiter = emiter

    def Le(self, hitpoint): #FIXME --- Tip:yes no in hitpoint
        raise ValueError("Not yet implemented")
        if self._emiter:
            raise ValueError("Not yet implemented")
        else:
            return Spectrum(False, (0.0, 0.0, 0.0))

    def f(self, hp):
        spectrum = self._spectrum.zero_spectrum()
        for c in self._brdfs:
            spectrum = spectrum + c.brdf(hp) 
        
        #TODO -- set constraint that spectrum can be max 1.0
        hp.f_spectrum = spectrum
        return spectrum 

    #eax pointer to hitpoint
    def f_asm(self, runtimes, assembler, structures):
        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            spectrum temp_spectrum 
            float zero = 0.0
            uint32 hp_ptr
            #CODE
            mov dword [hp_ptr], eax ;save pointer to hitpoint
            macro eq32 xmm0 = zero
            mov eax, temp_spectrum
            macro spectrum eax = xmm0 * eax 
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
        ret

        """
        mc = assembler.assemble(code, True)
        #print(code)
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


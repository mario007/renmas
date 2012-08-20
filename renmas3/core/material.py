import platform
from random import random

from .shade_point import ShadePoint
from ..materials import BRDF, BRDFSampling, BTDF, BTDFSampling

class Material:
    def __init__(self, spectrum):
        self._brdfs = []
        self._samplers = []

        self._btdf_sampler = None
        self._btdf = None

        self._emission = None 
        self._spectrum = spectrum

    def add(self, obj): #brdf or btdf or sampler 
        if isinstance(obj, BRDF):
            self._brdfs.append(obj)
        elif isinstance(obj, BRDFSampling):
            self._samplers.append(obj)
        elif isinstance(obj, BTDF):
            self._btdf = obj
        elif isinstance(obj, BTDFSampling):
            self._btdf_sampler = obj

    def set_emission(self, emission):
        self._emission = emission 

    def next_direction_bsdf(self, shadepoint):
        pass

    def next_direction_bsdf_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def next_direction_btdf(self, shadepoint):
        pass

    def next_direction_btdf_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def next_direction_brdf(self, shadepoint):
        pass

    def next_direction_brdf_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def Le(self, sp):
        if self._emission:
            pass #TODO
        else:
            return self._spectrum.zero_spectrum()

    def Le_asm(self, runtimes, assembler):
        pass #TODO

    def brdf(self, sp):
        spectrum = self._spectrum.zero_spectrum()
        for c in self._brdfs:
            spectrum = spectrum + c.brdf(sp)
        
        spectrum = spectrum * sp.normal.dot(sp.wi)
        spectrum.clamp(0.0, 0.99)
        sp.f_spectrum = spectrum
        return spectrum

    #eax pointer to hitpoint
    def brdf_asm(self, runtimes, assembler):
        bits = platform.architecture()[0]
        code = "#DATA \n" + self._spectrum.struct() + ShadePoint.struct() + """
            spectrum temp_spectrum 
            float low = 0.00
            float high = 0.99
        """
        if bits == '64bit':
            code += """
            uint64 hp_ptr
            #CODE
            mov qword [hp_ptr], rax ;save pointer to shadepoint
            """
        else:
            code += """
            uint32 hp_ptr
            #CODE
            mov dword [hp_ptr], eax ;save pointer to shadepoint
            """
        code += """
            macro mov eax, temp_spectrum
            macro call zero xmm0
            macro spectrum eax = xmm0
        """
        for c in self._brdfs:
            if bits == '64bit':
                code += "mov rax, qword [hp_ptr] \n" 
            else:
                code += "mov eax, dword [hp_ptr] \n" 
            label = 'comp' + str(id(c))
            c.brdf_asm(runtimes, assembler, label) #eax pointer to reflectance
            code += "call " + label
            code += """
                macro mov ebx, temp_spectrum 
                macro spectrum ebx = ebx + eax
            """
        if bits == '64bit':
            code += "mov rbx, qword [hp_ptr]\n"
        else:
            code += "mov ebx, dword [hp_ptr]\n"
        code += """
        macro mov eax, temp_spectrum
        macro dot xmm0 = ebx.shadepoint.normal * ebx.shadepoint.wi {xmm6, xmm7}
        macro spectrum eax = xmm0 * eax 

        macro lea ecx, dword [ebx + shadepoint.f_spectrum]
        macro spectrum ecx = eax
        macro eq32 xmm0 = low
        macro eq32 xmm1 = high
        macro spectrum clamp ecx 
        ret

        """
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        self.brdf_asm_name = name = "brdf" + str(id(self))
        for r in runtimes:
            r.load(name, mc)

    def btdf(self, hp):
        pass

    #eax pointer to hitpoint
    def btdf_asm(self, runtimes, assembler):
        pass

    def convert_spectrums(self, col_mgr):
        self._spectrum = col_mgr.convert_spectrum(self._spectrum)
        for c in self._brdfs:
            c.convert_spectrums(col_mgr)
        if self._btdf is not None:
            self._btdf.convert_spectrums(col_mgr)


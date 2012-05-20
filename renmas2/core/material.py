
from random import random

from ..materials import BRDF, Sampling, BTDF, BTDFSampling
from .spectrum import Spectrum
import renmas2.switch as proc

class Material:
    def __init__(self, spectrum):
        self._brdfs = []
        self._samplers = []

        self._btdf_sampler = None
        self._btdf = None

        self._emiter = None
        self._spectrum = spectrum
        self._counter = 0

        #caching machine code to speed up compilation of shader
        self._brdf_mc = None
        self._next_dir_mc = None
        self._next_brdf_mc = None

    def add(self, obj): #brdf or btdf or sampler 
        if isinstance(obj, BRDF):
            self._brdfs.append(obj)
        elif isinstance(obj, Sampling):
            self._samplers.append(obj)
        elif isinstance(obj, BTDF):
            self._btdf = obj
        elif isinstance(obj, BTDFSampling):
            self._btdf_sampler = obj

        self._brdf_mc = None
        self._next_dir_mc = None
        self._next_brdf_mc = None

        #TODO -- btdf sampler Log!!!

    def set_emiter(self, emiter):
        self._emiter = emiter

    def Le(self, hitpoint): #FIXME --- Tip:yes no in hitpoint
        raise ValueError("Not yet implemented")
        if self._emiter:
            raise ValueError("Not yet implemented")
        else:
            return Spectrum(False, (0.0, 0.0, 0.0))

    def _tir(self, hitpoint):
        hp = hitpoint
        cosi = hp.normal.dot(hp.wo)
        if hp.fliped: # ray is inside object
            eta = self._btdf_sampler._eta_out / self._btdf_sampler._eta_in
        else:
            eta = self._btdf_sampler._eta_in / self._btdf_sampler._eta_out

        d = 1.0 - (1.0 - cosi*cosi) / (eta*eta)
        if d < 0.0:
            return True
        else:
            return False


    def next_direction(self, hitpoint):
        if len(self._samplers) == 0: raise ValueError("Missing sampler!!!")
        
        if len(self._samplers) == 1:
            self._samplers[0].next_direction(hitpoint)
        else:
            idx = int(len(self._samplers) * random())
            self._samplers[idx].next_direction(hitpoint)
        pdf = 0.0
        for s in self._samplers:
            pdf += s.pdf(hitpoint)
        hitpoint.pdf = pdf / len(self._samplers)

        self.f(hitpoint)

    def next_direction_btdf(self, hitpoint):
        self._btdf_sampler.next_direction(hitpoint)
        hitpoint.pdf = self._btdf_sampler.pdf(hitpoint)
        self.btdf(hitpoint)

    def next_direction_bsdf(self, hitpoint):
        # if it is not dielectric call brdf next direction
        if self._btdf is None or self._btdf_sampler is None:
            self.next_direction(hitpoint)
            return

        # Material is dielectric 
        # 1. check tir
        if self._tir(hitpoint):
            # use just reflection
            self.next_direction(hitpoint)
            return
        else:
            #cosi = hitpoint.ndotwi
            k = 0.04
            #P = k / 2.0 + (1 - k) * self._btdf._fresnel.schlick(hitpoint.ndotwi) 
            P = 0.05
            if random() < P:
                self.next_direction(hitpoint)
                hitpoint.f_spectrum = hitpoint.f_spectrum * (1/P)  
            else:
                self.next_direction_btdf(hitpoint)
                hitpoint.f_spectrum = hitpoint.f_spectrum * (1/(1.0-P)) 

    def next_direction_bsdf_asm(self, runtimes, structures, assembler):
        # if it is not dielectric call brdf next direction
        if self._btdf is None or self._btdf_sampler is None:
            self.next_direction_asm(runtimes, structures, assembler)
            return
        
        next_brdf = "bsdf_next_brdf" + str(abs(hash(self)))
        next_btdf = "bsdf_next_btdf" + str(abs(hash(self)))
        self.next_direction_asm(runtimes, structures, assembler, next_brdf)
        self.next_direction_btdf_asm(runtimes, structures, assembler, next_btdf)
        ASM = """ 
            #DATA
        """
        ASM += structures.structs(("hitpoint",))
        ASM += """
            float eta_out
            float eta_in
            float one = 1.0
            float P = 0.1
            uint32 hp_ptr
            float cosi
            #CODE
            mov dword [hp_ptr], eax ;save pointer to hitpoint
            macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo {xmm6, xmm7}
            macro eq32 cosi = xmm0 {xmm7}
            mov ebx, dword [eax + hitpoint.fliped]
            cmp ebx, 1
            jne _outside
            macro eq32 xmm1 = eta_out / eta_in
            jmp _next
            _outside:
            macro eq32 xmm1 = eta_in / eta_out
            _next:
            ; check for TIR
            macro eq32 xmm0 = xmm0 * xmm0 
            macro eq32 xmm1 = xmm1 * xmm1
            macro eq32 xmm2 = one - xmm0
            macro eq32 xmm2 = xmm2 / xmm1
            macro eq32 xmm3 = one - xmm2
            macro call zero xmm4
            macro if xmm3 > xmm4 goto _next2
            mov eax, dword [hp_ptr]
        """
        ASM += "call " + next_brdf + """ 
            ret
            _next2:
            macro call random
            macro if xmm0 < P goto _calc_brdf_next
            mov eax, dword [hp_ptr]
        """
        ASM += "call " + next_btdf + """ 
            macro eq32 xmm1 = one - P
            macro eq32 xmm0 = one / xmm1
            mov eax, dword [hp_ptr]
            lea ecx, dword [eax + hitpoint.f_spectrum]
            macro spectrum ecx = xmm0 * ecx
            ret

            _calc_brdf_next:
            mov eax, dword [hp_ptr]
        """
        ASM += "call " + next_brdf + """ 
            macro eq32 xmm0 = one / P
            mov eax, dword [hp_ptr]
            lea ecx, dword [eax + hitpoint.f_spectrum]
            macro spectrum ecx = xmm0 * ecx
            ret

        """

        mc = assembler.assemble(ASM, True)
        #print(code)
        #mc.print_machine_code()
        self.nd_asm_name = name = "material_ndir_bsdf" + str(hash(self))
        for r in runtimes:
            ds = r.load(name, mc)
            ds["eta_out"] = self._btdf_sampler._eta_out
            ds["eta_in"] = self._btdf_sampler._eta_in

    def next_direction_btdf_asm(self, runtimes, structures, assembler, label=None):
        if self._btdf is None: raise ValueError("Missing btdf!!!")
        if self._btdf_sampler is None: raise ValueError("Missing btdf sampler!!!")

        label_btdf = "mat_next_btdf" + str(abs(hash(self)))
        self._next_btdf_asm(runtimes, assembler, structures, label_btdf)

        self._btdf_sampler.next_direction_asm(runtimes, structures, assembler)
        sampling_name = self._btdf_sampler.nd_asm_name

        ASM = """ 
            #DATA
        """
        ASM += structures.structs(("hitpoint",))
        ASM += "uint32 sampling_ptrs \n"
        ASM += """
            uint32 hp_ptr
            #CODE
        """
        if label is not None:
            ASM += "global " + label + ":\n"
        ASM += """
            mov dword [hp_ptr], eax ;save pointer to hitpoint
            ; generate direction 
            call dword [sampling_ptrs]
            mov eax, dword [hp_ptr]

        """
        ASM += self._btdf_sampler.pdf_asm()
        ASM += """
            macro eq32 eax.hitpoint.pdf = xmm0 {xmm7}
            mov eax, dword [hp_ptr]
        """
        ASM += "call " + label_btdf + """
            ret
        """

        mc = assembler.assemble(ASM, True)
        #print(code)
        #mc.print_machine_code()
        self.nd_asm_name = name = "material_ndir_btdf" + str(hash(self))
        for r in runtimes:
            ds = r.load(name, mc)
            ds["sampling_ptrs"] = r.address_module(sampling_name)
            self._btdf_sampler.pdf_ds(ds)

    #eax pointer to hitpoint
    def next_direction_asm(self, runtimes, structures, assembler, label=None):
        if len(self._samplers) == 0: raise ValueError("Missing sampler!!!")
        
        #TODO Random int function ---- insted random float needed for selecting sampler
        self._sampling_names = []
        for s in self._samplers:
            s.next_direction_asm(runtimes, structures, assembler)
            self._sampling_names.append(s.nd_asm_name)

        label_brdf = "mat_next_brdf" + str(abs(hash(self)))
        self._next_brdf_asm(runtimes, assembler, structures, label_brdf)

        ASM = """ 
        #DATA
        """
        ASM += structures.structs(("hitpoint",)) + """
        float zero = 0.0
        float pdf
        float inv_c
        """
        ASM += "uint32 sampling_ptrs[" + str(len(self._samplers)) + "]\n"
        ASM += "float nsamplers = " + str(float(len(self._samplers))) + "\n"
        ASM += "float nsamplers2 = " + str(float(len(self._samplers)) - 0.01) + "\n"
        ASM += """
        uint32 hp_ptr
        #CODE
        """
        if label is not None:
            ASM += "global " + label + ":\n"
        ASM += """
        mov dword [hp_ptr], eax ;save pointer to hitpoint
        ; generate direction 
        """
        if len(self._samplers) == 1:
            ASM += """
            call dword [sampling_ptrs]
            """
        else:
            ASM += """
            macro call random
            macro eq32 xmm0 = xmm0 * nsamplers
            macro call zero xmm1
            macro call maxss xmm0, xmm1
            macro eq32 xmm3 = nsamplers2
            macro call minss xmm0, xmm3
            """
            if proc.AVX:
                ASM += "vcvttss2si ecx, xmm0 \n"
            else:
                ASM += "cvttss2si ecx, xmm0 \n"
            ASM += """
                mov eax, dword [hp_ptr]
                call dword [sampling_ptrs + 4*ecx]
            """

        ASM += """
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
            mov eax, dword [hp_ptr]
        """
        ASM += "call " + label_brdf + """
            ret
        """

        mc = assembler.assemble(ASM, True)
        #print(code)
        #mc.print_machine_code()
        self.nd_asm_name = name = "material_ndir_brdf" + str(hash(self))
        for r in runtimes:
            ds = r.load(name, mc)
            ds["inv_c"] = 1.0 / len(self._samplers)
            ds["sampling_ptrs"] = tuple([r.address_module(name) for name in self._sampling_names])
            for s in self._samplers:
                s.pdf_ds(ds)

    def f(self, hp):
        spectrum = self._spectrum.zero_spectrum()
        for c in self._brdfs:
            spectrum = spectrum + c.brdf(hp)
        spectrum = spectrum * hp.ndotwi
        
        #TODO -- set constraint that spectrum can be max 1.0 -- clamp
        hp.f_spectrum = spectrum
        hp.f_spectrum.clamp(0.0, 0.99)
        return spectrum 

    def btdf(self, hp):
        #TODO atenuation
        if self._btdf is None: return self._spectrum.zero_spectrum()
        spectrum = self._btdf.btdf(hp) * hp.ndotwi

        hp.f_spectrum = spectrum
        hp.f_spectrum.clamp(0.0, 0.99)
        return spectrum

    def btdf_asm(self, runtimes, assembler, structures):

        code = self._btdf_asm_code(runtimes, assembler, structures)
        mc = assembler.assemble(code, True)

        #print(code)
        #mc.print_machine_code()
        self.btdf_asm_name = name = "material_btdf" + str(abs(hash(self)))
        self._btdf_ds = []
        for r in runtimes:
            self._btdf_ds.append(r.load(name, mc))
        
        for ds in self._btdf_ds:
            self._btdf.populate_ds(ds)

    #eax pointer to hitpoint
    def f_asm(self, runtimes, assembler, structures):
        
        code = self._brdf_asm_code(runtimes, assembler, structures)
        mc = assembler.assemble(code, True)

        #print(code)
        #mc.print_machine_code()
        self.f_asm_name = name = "material_brdf" + str(hash(self))
        self.ds = []
        for r in runtimes:
            self.ds.append(r.load(name, mc))

        for c in self._brdfs:
            for ds in self.ds:
                c.populate_ds(ds)

    #eax pointer to hitpoint
    def _next_btdf_asm(self, runtimes, assembler, structures, label):

        code = self._btdf_asm_code(runtimes, assembler, structures, label)
        mc = assembler.assemble(code, True)
        #print(code)
        #mc.print_machine_code()

        name = "mat_next_btdf_dir" + str(abs(hash(self)))
        self._next_btdf_ds = []
        for r in runtimes:
            self._next_btdf_ds.append(r.load(name, mc))
        
        for ds in self._next_btdf_ds:
            self._btdf.populate_ds(ds)

    #eax pointer to hitpoint
    def _next_brdf_asm(self, runtimes, assembler, structures, label):
        
        code = self._brdf_asm_code(runtimes, assembler, structures, label)
        mc = assembler.assemble(code, True)
        name = "mat_next_brdf_dir" + str(abs(hash(self)))
        self._next_ds = []
        for r in runtimes:
            self._next_ds.append(r.load(name, mc))

        for c in self._brdfs:
            for ds in self._next_ds:
                c.populate_ds(ds)

    #eax pointer to hitpoint
    def _brdf_asm_code(self, runtimes, assembler, structures, label=None):
        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            spectrum temp_spectrum 
            uint32 hp_ptr
            float low = 0.00
            float high = 0.99
            #CODE
        """
        if label is not None:
            code += "global " + label + ":\n"
        code += """
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
        macro eq32 xmm0 = ebx.hitpoint.ndotwi
        macro spectrum eax = xmm0 * eax 

        lea ecx, dword [ebx + hitpoint.f_spectrum]
        macro spectrum ecx = eax
        macro eq32 xmm0 = low
        macro eq32 xmm1 = high
        macro spectrum clamp ecx 
        ret

        """
        return code

    #eax pointer to hitpoint
    # eax -- return transmittance
    def _btdf_asm_code(self, runtimes, assembler, structures, label=None):
        code = """
            #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            spectrum temp_spectrum 
            uint32 hp_ptr
            float low = 0.00
            float high = 0.99
            #CODE
        """
        if label is not None:
            code += "global " + label + ":\n"
        code += """
            mov dword [hp_ptr], eax ;save pointer to hitpoint
            mov eax, temp_spectrum
            macro call zero xmm0
            macro spectrum eax = xmm0
            mov eax, dword [hp_ptr]
        """
        code += self._btdf.btdf_asm(runtimes, assembler, structures)
        code += """
        mov ebx, temp_spectrum
        macro spectrum ebx = ebx + eax

        mov ecx, dword [hp_ptr]
        macro eq32 xmm0 = ecx.hitpoint.ndotwi
        macro spectrum ebx = xmm0 * ebx 

        lea edx, dword [ecx + hitpoint.f_spectrum]
        macro spectrum edx = ebx 
        macro eq32 xmm0 = low
        macro eq32 xmm1 = high
        macro spectrum clamp edx 
        ret

        """
        return code

    def convert_spectrums(self, converter):
        self._spectrum = converter.convert_spectrum(self._spectrum)
        for c in self._brdfs:
            c.convert_spectrums(converter)
        if self._btdf is not None:
            self._btdf.convert_spectrums(converter)


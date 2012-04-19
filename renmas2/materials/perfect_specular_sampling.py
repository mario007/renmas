
from .sampling import Sampling

class PerfectSpecularSampling(Sampling):
    def __init__(self):
        pass

    def next_direction(self, hitpoint):
        hp = hitpoint
        ndotwo = hp.normal.dot(hp.wo)
        r = hp.normal * ndotwo * 2.0 - hp.wo
        hp.wi = r
        hp.ndotwi = hp.normal.dot(r)
        hp.specular = 89 #special case - delta distribution

    # eax - pointer to hitpoint
    def next_direction_asm(self, runtimes, structures, assembler):
        code = """ 
        #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            float two = 2.0
            #CODE
            macro eq128 xmm0 = eax.hitpoint.normal
            macro eq128 xmm1 = eax.hitpoint.wo
            macro dot xmm2 = xmm0 * xmm1 {xmm6, xmm7}
            macro eq32 xmm2 = xmm2 * two
            macro broadcast xmm2 = xmm2[0]
            macro eq128 xmm3 = xmm0 * xmm2 - xmm1
            macro dot xmm4 = xmm0 * xmm3 {xmm6, xmm7}
            macro eq128 eax.hitpoint.wi = xmm3 {xmm7}  
            macro eq32 eax.hitpoint.ndotwi = xmm4 {xmm7}
            mov dword [eax + hitpoint.specular], 89
            ret

        """

        self.nd_asm_name = name = "perfect_specular_sampling" + str(hash(self))
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        #print(code)
        self._ds = []
        for r in runtimes:
            self._ds.append(r.load(name, mc))

    def pdf(self, hitpoint):
        if hitpoint.specular == 89:
            return 1.0
        else:
            return 0.0

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self):
        sufix = str(abs(hash(self)))
        ASM = ""
        ASM += "#DATA \n"
        ASM += "float one%s = 1.0 \n" % sufix
        ASM += "#CODE \n"
        ASM += "mov ebx, dword [eax + hitpoint.specular] \n"
        ASM += "cmp ebx, 89 \n"
        ASM += "je  specular_sample%s\n"  % sufix 
        ASM += "macro call zero xmm0 \n"
        ASM += "jmp end_specular%s \n" % sufix
        ASM += "specular_sample%s:\n" % sufix
        ASM += "macro eq32 xmm0 = one%s \n" % sufix
        ASM += "end_specular%s:\n" % sufix
        return ASM

    #populate ds
    def pdf_ds(self, ds):
        pass


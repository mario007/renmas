
import math
import renmas.maths

import renmas.utils as util

class SpecularSampling:
    def __init__(self):
        pass

    def get_sample(self, hitpoint):
        hp = hitpoint
        ndotwo = hp.normal.dot(hp.wo)
        r = hp.normal * ndotwo * 2.0 - hp.wo
        hp.wi = r
        hp.ndotwi = hp.normal.dot(r)
        hp.specular = True #special case
        
    def get_sample_asm(self, runtime):

        # eax - pointer to hitpoint
        asm_structs = renmas.utils.structs("hitpoint")

        ASM = """ 
        #DATA
        float two[4] = 2.0, 2.0, 2.0, 0.0
        """
        ASM += asm_structs + """
        #CODE
        macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo
        macro broadcast xmm1 = xmm0[0]
        macro eq128 xmm1 = xmm1 * two
        macro eq128 xmm1 = xmm1 * eax.hitpoint.normal
        macro eq128 xmm1 = xmm1 - eax.hitpoint.wo


        macro dot xmm4 = xmm1 * eax.hitpoint.normal 
        
        macro eq128 eax.hitpoint.wi = xmm1
        macro eq32 eax.hitpoint.ndotwi = xmm4
        mov dword [eax + hitpoint.specular], 14
        ret
        """

        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "brdf_specular" + str(util.unique())
        self.ds = runtime.load(name, mc)
        self.func_ptr = runtime.address_module(name) 

    def pdf(self, hitpoint):
        if hitpoint.specular:
            hitpoint.pdf = 1.0
        else:
            hitpoint.pdf = 0.0 

    def pdf_asm(self):
        prefix = "_" + str(hash(self)) + "_"
        
        # eax - pointer to hitpoint
        ASM = "#CODE \n" 
        ASM += "mov ebx, dword [eax + hitpoint.specular] \n"
        ASM += "cmp ebx, 0 \n" #0-no specular sample
        ASM += "jne " + prefix + "spec_sample\n"
        ASM += "pxor xmm0, xmm0 \n" # put 0.0 in xmm0
        ASM += "jmp " + prefix + "end_spec \n"
        ASM += prefix + "spec_sample: \n"
        ASM += "pcmpeqw xmm0, xmm0 \n" # generate 1.0 in xmm0
        ASM += "pslld xmm0, 25 \n"
        ASM += "psrld xmm0, 2 \n"
        ASM += prefix + "end_spec: \n"

        return ASM


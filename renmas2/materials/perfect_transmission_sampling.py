
from math import sqrt
from .sampling import BTDFSampling

class PerfectTransmissionSampling(BTDFSampling):
    def __init__(self, eta_in, eta_out):

        self._eta_in = float(eta_in)
        self._eta_out = float(eta_out)

    def _set_eta_in(self, value):
        self._eta_in = float(value)
    def _get_eta_in(self):
        return self._eta_in
    eta_in = property(_get_eta_in, _set_eta_in)

    def _set_eta_out(self, value):
        self._eta_out = float(value)
    def _get_eta_out(self):
        return self._eta_out
    eta_out = property(_get_eta_out, _set_eta_out)

    def next_direction(self, hitpoint):

        hp = hitpoint
        cosi = hp.normal.dot(hp.wo)
        if hp.fliped: # ray is inside object
            eta = self._eta_out / self._eta_in
        else:
            eta = self._eta_in / self._eta_out
        
        cost = sqrt(1.0 - (1.0 - cosi * cosi) / (eta*eta))
        
        t = (hp.wo * -1.0) * (1.0/eta) - hp.normal * (cost - cosi / eta)

        hp.wi = t
        hp.ndotwi = (hp.normal * -1.0).dot(t)
        hp.specular = 65 #special case - delta distribution

    # eax - pointer to hitpoint
    def next_direction_asm(self, runtimes, structures, assembler):
        code = """ 
        #DATA
        """
        code += structures.structs(('hitpoint',)) + """
            float eta_in
            float eta_out
            float one = 1.0
            float minus_one[4] = -1.0, -1.0, -1.0, 0.0
            #CODE
            macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo {xmm6, xmm7}
            mov ebx, dword [eax + hitpoint.fliped]
            cmp ebx, 1
            je _next
            macro eq32 xmm1 = eta_in / eta_out
            jmp _next2
            _next:
            macro eq32 xmm1 = eta_out / eta_in

            _next2:
            macro eq32 xmm2 = xmm0 * xmm0
            macro eq32 xmm3 = xmm1 * xmm1
            macro eq32 xmm4 = one - xmm2
            macro eq32 xmm4 = xmm4 / xmm3
            macro eq32 xmm5 = one - xmm4
            macro call sqrtss xmm5, xmm5
            ; xmm5 = cost
            macro eq32 xmm2 = xmm0 / xmm1
            macro eq32 xmm3 = xmm5 - xmm2
            macro broadcast xmm3 = xmm3[0]
            macro eq128 xmm3 = xmm3 * eax.hitpoint.normal

            macro eq32 xmm6 = one / xmm1
            macro broadcast xmm6 = xmm6[0]
            macro eq128 xmm7 = eax.hitpoint.wo * minus_one * xmm6 - xmm3

            macro eq128 eax.hitpoint.wi = xmm7 {xmm2}  
            macro eq128 xmm2 = eax.hitpoint.normal * minus_one
            macro dot xmm2 = xmm2 * xmm7 {xmm3, xmm6}
            macro eq32 eax.hitpoint.ndotwi = xmm2 {xmm3}

            mov dword [eax + hitpoint.specular], 65 
            ret

        """

        self.nd_asm_name = name = "perfect_transmission_sampling" + str(hash(self))
        mc = assembler.assemble(code, True)
        #mc.print_machine_code()
        #print(code)
        self._ds = []
        for r in runtimes:
            ds = r.load(name, mc)
            ds['eta_in'] = self._eta_in
            ds['eta_out'] = self._eta_out
            self._ds.append(ds)

    def pdf(self, hitpoint):
        if hitpoint.specular == 65:
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
        ASM += "cmp ebx, 65 \n"
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


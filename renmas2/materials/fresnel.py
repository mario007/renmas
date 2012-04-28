
from math import sqrt

class FresnelConductor:
    def __init__(self, n, k):
        
        self._n = n
        self._k = k

    @classmethod
    def conv_f0(cls, F0):
        n = F0.zero_spectrum()
        k = F0.zero_spectrum()

        if F0.sampled:
            samples = [(1.0+sqrt(s))/(1.0-sqrt(s)) for s in F0.samples]
            n.samples = samples
        else:
            n.r = (1.0 + sqrt(F0.r)) / (1.0 - sqrt(F0.r)) 
            n.g = (1.0 + sqrt(F0.g)) / (1.0 - sqrt(F0.g)) 
            n.b = (1.0 + sqrt(F0.b)) / (1.0 - sqrt(F0.b)) 

        if F0.sampled:
            samples = [2.0*sqrt(s/(1.0-s)) for s in F0.samples]
            k.samples = samples
        else:
            k.r = 2.0 * sqrt(F0.r / (1.0 - F0.r)) 
            k.g = 2.0 * sqrt(F0.g / (1.0 - F0.g)) 
            k.b = 2.0 * sqrt(F0.b / (1.0 - F0.b)) 

        return (n,k)


    def evaluate(self, hp):

        cosi = hp.normal.dot(hp.wo)

        pass

    # return spectrum is in eax
    def evaluate_asm(self):
        pass

class FresnelDielectric:
    def __init__(self, eta_in, eta_out):
        self._eta_in = eta_in
        self._eta_out = eta_out
        self._avg_eta_in = self._approx_n(eta_in)
        self._avg_eta_out = self._approx_n(eta_out)

    @classmethod
    def conv_f0(cls, F0):
        n = F0.zero_spectrum()

        if F0.sampled:
            samples = [(1.0+sqrt(s))/(1.0-sqrt(s)) for s in F0.samples]
            n.samples = samples
        else:
            n.r = (1.0 + sqrt(F0.r)) / (1.0 - sqrt(F0.r)) 
            n.g = (1.0 + sqrt(F0.g)) / (1.0 - sqrt(F0.g)) 
            n.b = (1.0 + sqrt(F0.b)) / (1.0 - sqrt(F0.b)) 
        return n

    def schlick(self, cosi):
        nt = self._avg_eta_in
        ro = ((nt - 1.0) * (nt - 1.0)) / ((nt + 1.0) * (nt + 1.0)) 
        c = 1.0 - cosi
        R = ro + (1.0 - ro) * c * c * c * c * c
        return R

    def _approx_n(self, n):
        if n.sampled:
            avg = 0.0
            for s in n.samples:
                avg += s
            return avg / len(n.samples)
        else:
            avg = (n.r + n.g + n.b) / 3.0
            return avg

    def evaluate(self, hp):

        cosi = hp.normal.dot(hp.wo)
        if hp.fliped: # ray is inside object
            etai = self._eta_out
            etat = self._eta_in
            eta = self._avg_eta_out / self._avg_eta_in
        else:
            etai = self._eta_in
            etat = self._eta_out
            eta = self._avg_eta_in / self._avg_eta_out

        d = 1.0 - (1.0 - cosi*cosi) / (eta*eta)
        if d < 0.0: #TIR
            return self._eta_in.zero_spectrum().set(1.0)

        if hp.normal.dot(hp.wi) < 0.0:
            cost = hp.wi.dot(hp.normal * -1.0)
        else:
            cost = hp.wi.dot(hp.normal)
        
        etat_cosi = etat * cosi
        etai_cost = etai * cost
        r_para = (etat_cosi - etai_cost).div_spectrum(etat_cosi + etai_cost)

        etai_cosi = etai * cosi
        etat_cost = etat * cost

        r_oko = (etai_cosi - etat_cost).div_spectrum(etai_cosi + etat_cost)


        fr = (r_para.mix_spectrum(r_para) + r_oko.mix_spectrum(r_oko)) * 0.5

        return fr

    # eax is ptr to hitpoint
    def evaluate_asm(self):
        sufix = "fresnel" + str(abs(hash(self)))

        ASM = ""
        ASM += "#DATA \n"
        ASM += "spectrum  eta_in%s \n" % sufix 
        ASM += "spectrum  eta_out%s \n" % sufix 
        ASM += "spectrum one_spectrum%s \n" % sufix
        ASM += "spectrum  ret_spectrum%s \n" % sufix 
        ASM += "float avg_eta_in%s \n" % sufix
        ASM += "float avg_eta_out%s \n" % sufix
        ASM += "float minus_one%s[4] = -1.0, -1.0, -1.0, 0.0 \n" % sufix
        ASM += "float one%s = 1.0 \n" % sufix
        ASM += "float cosi%s \n" % sufix
        ASM += "float cost%s \n" % sufix
        ASM += "#CODE \n"
        ASM += "macro dot xmm0 = eax.hitpoint.normal * eax.hitpoint.wo {xmm6, xmm7}\n"
        ASM += "macro eq32 cosi%s = xmm0 {xmm7} \n" % sufix
        ASM += "mov ebx, dword [eax + hitpoint.fliped] \n"
        ASM += "cmp ebx, 1 \n"
        ASM += "jne _outside%s \n" % sufix
        ASM += "mov ecx, eta_out%s \n" % sufix
        ASM += "mov edx, eta_in%s \n" % sufix
        ASM += "macro eq32 xmm1 = avg_eta_out%s / avg_eta_in%s \n" % (sufix, sufix)
        ASM += "jmp _next%s \n" % sufix

        ASM += "_outside%s: \n" % sufix
        ASM += "mov ecx, eta_in%s \n" % sufix
        ASM += "mov edx, eta_out%s \n" % sufix
        ASM += "macro eq32 xmm1 = avg_eta_in%s / avg_eta_out%s \n" % (sufix, sufix)

        ASM += "_next%s: \n" % sufix
        # check for TIR
        ASM += "macro eq32 xmm2 = xmm0 * xmm0 \n"
        ASM += "macro eq32 xmm1 = xmm1 * xmm1 \n"
        ASM += "macro eq32 xmm3 = one%s - xmm2 \n" % sufix
        ASM += "macro eq32 xmm3 = xmm3 / xmm1 \n"
        ASM += "macro eq32 xmm4 = one%s - xmm3 \n" % sufix
        ASM += "macro call zero xmm5 \n"
        ASM += "macro if xmm4 > xmm5 goto _calc1%s \n" % sufix
        ASM += "mov eax, one_spectrum%s \n" % sufix
        ASM += "jmp _end%s \n" % sufix

        ASM += "_calc1%s: \n" % sufix
        ASM += "macro dot xmm4 = eax.hitpoint.normal * eax.hitpoint.wi {xmm6, xmm7}\n"
        ASM += "macro if xmm4 < xmm5 goto _flip_normal%s \n" % sufix
        ASM += "macro eq128 xmm3 = eax.hitpoint.normal \n"
        ASM += "jmp _end_fliping%s \n" % sufix
        ASM += "_flip_normal%s: \n" % sufix
        ASM += "macro eq128 xmm3 = eax.hitpoint.normal * minus_one%s \n" % sufix
        ASM += "_end_fliping%s: \n" % sufix
        ASM += "macro dot xmm4 = xmm3 * eax.hitpoint.wi {xmm6, xmm7} \n"
        ASM += "macro eq32 cost%s = xmm4 {xmm7} \n" % sufix

        ASM += "macro eq32 xmm0 = cosi%s \n" % sufix 
        ASM += "macro eq32 xmm1 = cost%s \n" % sufix

        #evaluate fresnel - result is in eax
        ASM += fresnel_evaluate_asm(sufix)

        ASM += "_end%s: \n" % sufix

        return ASM

    def populate_ds(self, ds):
        sufix = "fresnel" + str(abs(hash(self)))
        ds["eta_in" + sufix + ".values"] = self._eta_in.to_ds()
        ds["eta_out" + sufix + ".values"] = self._eta_out.to_ds() 
        ds["one_spectrum" + sufix + ".values"] = self._eta_in.zero_spectrum().set(1.0).to_ds() 
        ds["avg_eta_in" + sufix] = self._avg_eta_in
        ds["avg_eta_out" + sufix] = self._avg_eta_out

    def convert_spectrums(self, converter):
        self._eta_in = converter.convert_spectrum(self._eta_in)
        self._eta_out = converter.convert_spectrum(self._eta_out)

        self._avg_eta_in = self._approx_n(self._eta_in)
        self._avg_eta_out = self._approx_n(self._eta_out)


# xmm0 = cosi , xmm1 = cost, ecx = etai, edx = etat
def fresnel_evaluate_asm(sufix):

    ASM = ""
    ASM += "#DATA \n"
    ASM += "spectrum  temp1%s \n" % sufix 
    ASM += "spectrum  temp2%s \n" % sufix 
    ASM += "spectrum temp3%s \n" % sufix
    ASM += "spectrum  temp4%s \n" % sufix 
    ASM += "spectrum  temp5%s \n" % sufix 
    ASM += "float _half_one%s = 0.5 \n" % sufix
    ASM += "float _cosi%s \n" % sufix
    ASM += "float _cost%s \n" % sufix
    ASM += "#CODE \n"

    ASM += "macro eq32 _cosi%s = xmm0 {xmm7} \n" % sufix
    ASM += "macro eq32 _cost%s = xmm1 {xmm7} \n" % sufix

    ASM += "mov eax, temp1%s \n" % sufix
    ASM += "macro spectrum eax = xmm0 * edx \n"
    ASM += "macro eq32 xmm0 = _cost%s \n" % sufix
    ASM += "mov ebx, temp2%s \n" % sufix
    ASM += "macro spectrum ebx = xmm0 * ecx \n"

    ASM += "mov eax, temp3%s \n" % sufix
    ASM += "mov ebx, temp1%s \n" % sufix
    ASM += "mov edi, temp2%s \n" % sufix
    ASM += "macro spectrum eax = ebx - edi \n"
    ASM += "mov eax, temp4%s \n" % sufix
    ASM += "macro spectrum eax = ebx + edi \n"
    ASM += "mov eax, temp5%s \n" % sufix
    ASM += "mov ebx, temp3%s \n" % sufix
    ASM += "mov edi, temp4%s \n" % sufix
    ASM += "macro spectrum eax = ebx / edi \n"

    ASM += "macro eq32 xmm0 = _cosi%s \n" % sufix
    ASM += "mov eax, temp1%s \n" % sufix
    ASM += "macro spectrum eax = xmm0 * ecx \n"
    ASM += "macro eq32 xmm0 = _cost%s \n" % sufix
    ASM += "mov ebx, temp2%s \n" % sufix
    ASM += "macro spectrum ebx = xmm0 * edx \n"
    ASM += "mov eax, temp3%s \n" % sufix
    ASM += "mov ebx, temp1%s \n" % sufix
    ASM += "mov edi, temp2%s \n" % sufix
    ASM += "macro spectrum eax = ebx - edi \n"
    ASM += "mov eax, temp4%s \n" % sufix
    ASM += "macro spectrum eax = ebx + edi \n"
    ASM += "mov eax, temp1%s \n" % sufix
    ASM += "mov ebx, temp3%s \n" % sufix
    ASM += "mov edi, temp4%s \n" % sufix
    ASM += "macro spectrum eax = ebx / edi \n"

    ASM += "mov eax, temp5%s \n" % sufix
    ASM += "macro spectrum eax = eax * eax \n"
    ASM += "mov eax, temp1%s \n" % sufix
    ASM += "macro spectrum eax = eax * eax \n"
    ASM += "mov eax, temp2%s \n" % sufix
    ASM += "mov ebx, temp5%s \n" % sufix
    ASM += "mov edi, temp1%s \n" % sufix
    ASM += "macro spectrum eax = ebx + edi \n"
    ASM += "macro eq32 xmm0 = _half_one%s\n" % sufix
    ASM += "macro spectrum eax = xmm0 * eax \n"
    ASM += ""

    return ASM


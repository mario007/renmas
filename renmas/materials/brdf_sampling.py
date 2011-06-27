import random
import math
import renmas.maths

import renmas.utils as util

class HemisphereCos:
    def __init__(self, e=1):
        self.e = e
        self.ie = 1.0 / (e + 1.0)
        self.invpi = 1.0 / math.pi
        self.func_ptr = None

    def get_sample(self, hitpoint):
        r1 = random.random()
        r2 = random.random()

        phi = 2.0 * math.pi * r1
        # savjet phar  - 1 - r2 mozemo samo sa r2 zamijeniti jer je r random izmedu 0 i 1 
        #cos_theta = math.pow(1.0 - r2, 1.0/(self.e + 1.0))
        cos_theta = math.pow(r2, self.ie)
        sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)
        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        pu = sin_theta * cos_phi 
        pv = sin_theta * sin_phi
        pw = cos_theta

        w = hitpoint.normal
        tv = renmas.maths.Vector3(0.0034, 1.0, 0.0071)
        v = tv.cross(w)
        v.normalize()
        u = v.cross(w)

        ndir = u * pu + v * pv + w * pw 
        ndir.normalize()
        
        ndotwi = hitpoint.normal.dot(ndir)

        hitpoint.wi = ndir
        hitpoint.ndotwi = ndotwi

    def pdf(self, hitpoint):
        hitpoint.pdf = hitpoint.ndotwi * self.invpi

    def get_sample_asm(self, runtime):
        
        # eax - pointer to hitpoint
        asm_structs = renmas.utils.structs("hitpoint")
        util.load_func(runtime, "random")
        util.load_func(runtime, "fast_sincos_ps")

        if util.AVX:
            line1 = "vmovss xmm1, dword [ecx + 4*ebx] \n"
        else:
            line1 = "movss xmm1, dword [ecx + 4*ebx] \n"


        ASM = """ 
        #DATA
        """
        ASM += asm_structs + """
            float ie[4]
            float pi[4] = 3.14159265359, 3.14159265359, 3.14159265359, 3.14159265359
            float one[4] = 1.0, 1.0, 1.0, 1.0
            float two[4] = 2.0, 2.0, 2.0, 2.0
            float tvector[4] = 0.0034, 1.0, 0.0071, 0.0

            float pu[4]
            float pv[4]
            float pw[4]

            uint32 ptr_hp
            uint32 idx = 0

            #CODE
        """
        ASM += """
            mov dword [ptr_hp], eax
            sub dword [idx], 1
            js _calculate_samples
            _gen_direction:
            mov eax, dword [ptr_hp]
            macro eq128 xmm1 = eax.hitpoint.normal
            macro eq128 xmm7 = xmm1
            macro eq128 xmm0 = tvector
            
            """
        ASM += util.cross_product("xmm0", "xmm1", "xmm2", "xmm3") 
        ASM += util.normalization("xmm0", "xmm1", "xmm2") + """
            macro eq128 xmm1 = xmm7
            macro eq128 xmm6 = xmm0
        """
        ASM += util.cross_product("xmm0", "xmm1", "xmm2", "xmm3") 
        ASM += """
            mov ebx, dword [idx]
            mov ecx, pu
            ; in line we load pu, pv or pw
        """
        ASM += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm0 = xmm0 * xmm1 {xmm6, xmm7}
            mov ecx, pv
        """
        ASM += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm6 = xmm6 * xmm1 {xmm0, xmm7}
            macro eq128 xmm0 = xmm0 + xmm6
            mov ecx, pw
        """
        ASM += line1 + """
            macro broadcast xmm1 = xmm1[0]
            macro eq128 xmm1 = xmm1 * xmm7 {xmm0}
            macro eq128 xmm0 = xmm0 + xmm1 {xmm7}
        """
        ASM += util.normalization("xmm0", "xmm1", "xmm2") + """
            macro eq128 eax.hitpoint.wi = xmm0  
            macro dot xmm0 = xmm0 * xmm7
            macro eq32 eax.hitpoint.ndotwi = xmm0

            ret

            _calculate_samples:
            call random 

        """
        if self.e == 1:
            if util.AVX:
                ASM += "vsqrtps xmm0, xmm0 \n"
            else:
                ASM += "sqrtps xmm0, xmm0 \n"
        else:
            util.load_func(runtime, "fast_pow_ps")
            ASM += "macro eq128 xmm1 = ie \n" 
            ASM += "call fast_pow_ps \n"

        ASM += """
            macro eq128 pw = xmm0
            macro eq128 xmm0 = xmm0 * xmm0
            macro eq128 xmm1 = one - xmm0
            """
        if util.AVX:
            ASM += "vsqrtps xmm0, xmm1 \n"
        else:
            ASM += "sqrtps xmm0, xmm1 \n"

        ASM += """
            macro eq128 pu = xmm0
            macro eq128 pv = xmm0

            call random 

            macro eq128 xmm0 = xmm0 * pi
            macro eq128 xmm0 = xmm0 * two
            call fast_sincos_ps
            macro eq128 xmm0 = xmm0 * pv {xmm6}
            macro eq128 xmm6 = xmm6 * pu {xmm0}

            macro eq128 pv = xmm0
            macro eq128 pu = xmm6 
            mov dword [idx], 3
            jmp _gen_direction 
        """
        
        assembler = util.get_asm()
        mc = assembler.assemble(ASM, True)
        #mc.print_machine_code()
        name = "brdf_hemisphere" + str(util.unique())
        self.ds = runtime.load(name, mc)

        self.ds["ie"] = (self.ie, self.ie, self.ie, self.ie)

        #FIXME - add method to runtime class so we can ask runtime for address of module
        self.func_ptr = runtime.modules[name][0]


    def pdf_asm(self):

        name = "invpi" + str(hash(self))
        # eax - pointer to hitpoint
        ASM = "#DATA \n" 
        ASM += "float " + name + " = 0.318309886184 \n"
        ASM += "#CODE \n"
        ASM += "macro eq32 xmm0 = eax.hitpoint.ndotwi * " + name + "\n"

        return ASM


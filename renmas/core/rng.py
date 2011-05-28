
import random
from tdasm import Tdasm

import renmas.utils as util


class Rng:
    data = """
            #DATA
            uint32 cur_seed[4]
            uint32 mult[4] = 214013, 17405, 214013, 69069
            uint32 gadd[4] = 2531011, 10395331, 13737667, 1
            uint32 mask[4] = 0xFFFFFFFF, 0, 0xFFFFFFFF, 0
            uint32 masklo[4] = 0x00007FFF, 0x00007FFF, 0x00007FFF, 0x00007FFF
            uint32 _random_sign_mask[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
            float _random_flt[4] = 0.000000000465661287524, 0.000000000465661287524, 0.000000000465661287524, 0.000000000465661287524

        """

    @classmethod
    def random_int(cls, runtime, label):
        asm_code = cls.data + """
        #CODE
        """
        asm_code += " global " + label + ": " + """
            movdqa xmm0, oword [gadd]
            movdqa xmm1, oword [mult]
            movdqa xmm2, oword [mask]


            pshufd xmm4, oword [cur_seed], 10110001b
            movdqa xmm5, oword [cur_seed]
            pmuludq xmm5, xmm1
            pshufd xmm1, xmm1, 10110001b
            pmuludq xmm4, xmm1
            pand xmm5, xmm2
            pand xmm4, xmm2
            pshufd xmm4, xmm4, 10110001b
            por xmm5, xmm4
            paddd xmm0, xmm5

            movdqa oword [cur_seed], xmm0
            ret

        """

        avx_code = cls.data + """
        #CODE
        """
        avx_code += " global " + label + ": " + """
            vmovdqa xmm0, oword [gadd]
            vmovdqa xmm1, oword [mult]
            vmovdqa xmm2, oword [mask]


            vpshufd xmm4, oword [cur_seed], 10110001b
            vmovdqa xmm5, oword [cur_seed]
            vpmuludq xmm5, xmm5, xmm1
            vpshufd xmm1, xmm1, 10110001b
            vpmuludq xmm4, xmm4, xmm1
            vpand xmm5, xmm5, xmm2
            vpand xmm4, xmm4, xmm2
            vpshufd xmm4, xmm4, 10110001b
            vpor xmm5, xmm5, xmm4
            vpaddd xmm0, xmm0, xmm5

            vmovdqa oword [cur_seed], xmm0
            
            ret

        """
        
        asm = Tdasm()
        if util.AVX:
            mc = asm.assemble(avx_code, True)
        else:
            mc = asm.assemble(asm_code, True)

        name = "randomint" + str(util.unique())
        ds = runtime.load(name, mc)

        v1 = random.randint(0, 4000000000) 
        v2 = random.randint(0, 4000000000) 
        v3 = random.randint(0, 4000000000) 
        v4 = random.randint(0, 4000000000) 
        ds['cur_seed'] = (v1, v2, v3, v4) 
        return ds

    @classmethod
    def random_float(cls, runtime, label):
        asm_code = cls.data + """
        #CODE
        """
        asm_code += " global " + label + ": " + """
            movdqa xmm0, oword [gadd]
            movdqa xmm1, oword [mult]
            movdqa xmm2, oword [mask]


            pshufd xmm4, oword [cur_seed], 10110001b
            movdqa xmm5, oword [cur_seed]
            pmuludq xmm5, xmm1
            pshufd xmm1, xmm1, 10110001b
            pmuludq xmm4, xmm1
            pand xmm5, xmm2
            pand xmm4, xmm2
            pshufd xmm4, xmm4, 10110001b
            por xmm5, xmm4
            paddd xmm5, xmm0

            movdqa oword [cur_seed], xmm5

            ;convert to float
            pand xmm5, oword [_random_sign_mask]
            cvtdq2ps xmm0, xmm5
            mulps xmm0, oword [_random_flt]

            ret

        """

        avx_code = cls.data + """
        #CODE
        """
        avx_code += " global " + label + ": " + """
            vmovdqa xmm0, oword [gadd]
            vmovdqa xmm1, oword [mult]
            vmovdqa xmm2, oword [mask]


            vpshufd xmm4, oword [cur_seed], 10110001b
            vmovdqa xmm5, oword [cur_seed]
            vpmuludq xmm5, xmm5, xmm1
            vpshufd xmm1, xmm1, 10110001b
            vpmuludq xmm4, xmm4, xmm1
            vpand xmm5, xmm5, xmm2
            vpand xmm4, xmm4, xmm2
            vpshufd xmm4, xmm4, 10110001b
            vpor xmm5, xmm5, xmm4
            vpaddd xmm5, xmm5, xmm0

            vmovdqa oword [cur_seed], xmm5

            ;convert to float
            vpand xmm5, xmm5, oword [_random_sign_mask]
            vcvtdq2ps xmm0, xmm5
            vmulps xmm0, xmm0, oword [_random_flt]
            
            ret

        """
        
        asm = Tdasm()
        if util.AVX:
            mc = asm.assemble(avx_code, True)
        else:
            mc = asm.assemble(asm_code, True)
        
        name = "randomfloat" + str(util.unique())
        ds = runtime.load(name, mc)
        v1 = random.randint(0, 4000000000) 
        v2 = random.randint(0, 4000000000) 
        v3 = random.randint(0, 4000000000) 
        v4 = random.randint(0, 4000000000) 
        ds['cur_seed'] = (v1, v2, v3, v4) 



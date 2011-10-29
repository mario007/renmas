
import renmas2.switch as proc
from tdasm import Tdasm

def sin_ps():
    data = """
    #DATA

    uint32 _ps_am_inv_sign_mask[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_2_o_pi[4] = 0.63661977236, 0.63661977236, 0.63661977236, 0.63661977236
    uint32 _epi32_1[4] = 1, 1, 1, 1
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    uint32 _epi32_2[4] = 2, 2, 2, 2

    float _ps_sincos_p3[4] = -0.00468175413, -0.00468175413, -0.00468175413, -0.00468175413
    float _ps_sincos_p2[4] = 0.0796926262, 0.0796926262, 0.0796926262, 0.0796926262
    float _ps_sincos_p1[4] = -0.64596409750621,-0.64596409750621,-0.64596409750621,-0.64596409750621 
    float _ps_sincos_p0[4] = 1.570796326794896, 1.570796326794896, 1.570796326794896, 1.570796326794896
    """
    asm_code = data + """
    
    #CODE
    global fast_sin_ps:
    movaps xmm7, xmm0
    andps  xmm0, oword [ _ps_am_inv_sign_mask]
    andps  xmm7, oword [ _ps_am_sign_mask] 
    mulps	xmm0, oword [_ps_am_2_o_pi]

    pxor	xmm3, xmm3
    movdqa	xmm5, oword [_epi32_1]
    movaps	xmm4, oword [_ps_am_1]
    cvttps2dq	xmm2, xmm0
	pand	    xmm5, xmm2
	pcmpeqd	    xmm5, xmm3
    cvtdq2ps	xmm6, xmm2 
    pand        xmm2, oword [_epi32_2]
    pslld	    xmm2, 30

    subps	xmm0, xmm6
	minps	xmm0, xmm4
	subps	xmm4, xmm0
	andps	xmm0, xmm5
	andnps	xmm5, xmm4
	orps	xmm0, xmm5
    

    movaps	xmm1, xmm0
	mulps	xmm0, xmm0
	xorps	xmm2, xmm7
	orps	xmm1, xmm2
	movaps	xmm7, xmm0
    mulps	xmm0, oword [_ps_sincos_p3]
	addps	xmm0, oword [_ps_sincos_p2]
	mulps	xmm0, xmm7
	addps	xmm0, oword [_ps_sincos_p1]
	mulps	xmm0, xmm7
	addps	xmm0, oword [_ps_sincos_p0]
	mulps	xmm0, xmm1
	ret
    """
    avx_code = data + """

    #CODE
    global fast_sin_ps:
    vmovaps xmm7, xmm0
    vandps  xmm0, xmm0, oword [ _ps_am_inv_sign_mask]
    vandps  xmm7, xmm7, oword [ _ps_am_sign_mask] 
    vmulps	xmm0, xmm0, oword [_ps_am_2_o_pi]

    vpxor	xmm3, xmm3, xmm3
    vmovdqa	xmm5, oword [_epi32_1]
    vmovaps	xmm4, oword [_ps_am_1]
    vcvttps2dq	xmm2, xmm0
	vpand	    xmm5, xmm5, xmm2
	vpcmpeqd	xmm5, xmm5, xmm3
    vcvtdq2ps	xmm6, xmm2 
    vpand        xmm2, xmm2, oword [_epi32_2]
    vpslld	    xmm2, xmm2, 30

    vsubps	xmm0, xmm0, xmm6
	vminps	xmm0, xmm0, xmm4
	vsubps	xmm4, xmm4, xmm0
	vandps	xmm0, xmm0, xmm5
	vandnps	xmm5, xmm5, xmm4
	vorps	xmm0, xmm0, xmm5
    

    vmovaps	xmm1, xmm0
	vmulps	xmm0, xmm0, xmm0
	vxorps	xmm2, xmm2, xmm7
	vorps	xmm1, xmm1, xmm2
	vmovaps	xmm7, xmm0
    vmulps	xmm0, xmm0, oword [_ps_sincos_p3]
	vaddps	xmm0, xmm0, oword [_ps_sincos_p2]
	vmulps	xmm0, xmm0, xmm7
	vaddps	xmm0, xmm0, oword [_ps_sincos_p1]
	vmulps	xmm0, xmm0, xmm7
	vaddps	xmm0, xmm0, oword [_ps_sincos_p0]
	vmulps	xmm0, xmm0, xmm1
	ret
    """

    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    return mc

    #name = "fast_sin_ps"  
    #runtime.load(name, mc)


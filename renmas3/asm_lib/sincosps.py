
import renmas3.switch as proc
from tdasm import Tdasm

def sincos_ps():
    data = """
    #DATA
    uint32 _ps_am_inv_sign_mask[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679
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
    global fast_sincos_ps:
    movaps	xmm7, xmm0
    andps	xmm0, oword [_ps_am_inv_sign_mask]
    andps	xmm7, oword [_ps_am_sign_mask]
    mulps	xmm0, oword [_ps_am_2_o_pi]

    pxor	xmm3, xmm3
    movdqa	xmm5, oword [_epi32_1]
    movaps	xmm4, oword [_ps_am_1]

    cvttps2dq	xmm2, xmm0
    pand	xmm5, xmm2
    pcmpeqd	xmm5, xmm3
    movdqa	xmm3, oword [_epi32_1]
    movdqa	xmm1, oword [_epi32_2]
    cvtdq2ps	xmm6, xmm2
    paddd	xmm3, xmm2
    pand	xmm2, xmm1
    pand	xmm3, xmm1
    subps	xmm0, xmm6
    pslld	xmm2, 30 
    minps	xmm0, xmm4
    ;mov		eax, dword [esp + 4 + 16]
    ;mov		edx, dword [esp + 4 + 16 + 4]
    subps	xmm4, xmm0
    pslld	xmm3, 30 

    movaps	xmm6, xmm4
    xorps	xmm2, xmm7
    movaps	xmm7, xmm5
    andps	xmm6, xmm7
    andnps	xmm7, xmm0
    andps	xmm0, xmm5
    andnps	xmm5, xmm4
    movaps	xmm4, oword [_ps_sincos_p3]
    orps	xmm6, xmm7
    orps	xmm0, xmm5
    movaps	xmm5, oword [_ps_sincos_p2]

    movaps	xmm1, xmm0
    movaps	xmm7, xmm6
    mulps	xmm0, xmm0
    mulps	xmm6, xmm6
    orps	xmm1, xmm2
    orps	xmm7, xmm3
    movaps	xmm2, xmm0
    movaps	xmm3, xmm6
    mulps	xmm0, xmm4
    mulps	xmm6, xmm4
    movaps	xmm4, oword [_ps_sincos_p1]
    addps	xmm0, xmm5
    addps	xmm6, xmm5
    movaps	xmm5, oword [_ps_sincos_p0]
    mulps	xmm0, xmm2
    mulps	xmm6, xmm3
    addps	xmm0, xmm4
    addps	xmm6, xmm4
    mulps	xmm0, xmm2
    mulps	xmm6, xmm3
    addps	xmm0, xmm5
    addps	xmm6, xmm5
    mulps	xmm0, xmm1
    mulps	xmm6, xmm7

    ;movaps	dowrd [eax], xmm0 ; sinus(xmm0)
    ;movaps	dword [edx], xmm6 ; cosinus(xmm0)
    ret
    """

    avx_code = data + """
    #CODE
    global fast_sincos_ps:
    vmovaps	xmm7, xmm0
    vandps	xmm0, xmm0, oword [_ps_am_inv_sign_mask]
    vandps	xmm7, xmm7, oword [_ps_am_sign_mask]
    vmulps	xmm0, xmm0, oword [_ps_am_2_o_pi]

    vpxor	xmm3, xmm3, xmm3
    vmovdqa	xmm5, oword [_epi32_1]
    vmovaps	xmm4, oword [_ps_am_1]

    vcvttps2dq	xmm2, xmm0
    vpand	xmm5, xmm5, xmm2
    vpcmpeqd	xmm5, xmm5, xmm3
    vmovdqa	xmm3, oword [_epi32_1]
    vmovdqa	xmm1, oword [_epi32_2]
    vcvtdq2ps	xmm6, xmm2
    vpaddd	xmm3, xmm3, xmm2
    vpand	xmm2, xmm2, xmm1
    vpand	xmm3, xmm3, xmm1
    vsubps	xmm0, xmm0, xmm6
    vpslld	xmm2, xmm2, 30 
    vminps	xmm0, xmm0, xmm4
    ;mov		eax, dword [esp + 4 + 16]
    ;mov		edx, dword [esp + 4 + 16 + 4]
    vsubps	xmm4, xmm4, xmm0
    vpslld	xmm3, xmm3, 30 

    vmovaps	xmm6, xmm4
    vxorps	xmm2, xmm2, xmm7
    vmovaps	xmm7, xmm5
    vandps	xmm6, xmm6, xmm7
    vandnps	xmm7, xmm7, xmm0
    vandps	xmm0, xmm0, xmm5
    vandnps	xmm5, xmm5, xmm4
    vmovaps	xmm4, oword [_ps_sincos_p3]
    vorps	xmm6, xmm6, xmm7
    vorps	xmm0, xmm0, xmm5
    vmovaps	xmm5, oword [_ps_sincos_p2]

    vmovaps	xmm1, xmm0
    vmovaps	xmm7, xmm6
    vmulps	xmm0, xmm0, xmm0
    vmulps	xmm6, xmm6, xmm6
    vorps	xmm1, xmm1, xmm2
    vorps	xmm7, xmm7, xmm3
    vmovaps	xmm2, xmm0
    vmovaps	xmm3, xmm6
    vmulps	xmm0, xmm0, xmm4
    vmulps	xmm6, xmm6, xmm4
    vmovaps	xmm4, oword [_ps_sincos_p1]
    vaddps	xmm0, xmm0, xmm5
    vaddps	xmm6, xmm6, xmm5
    vmovaps	xmm5, oword [_ps_sincos_p0]
    vmulps	xmm0, xmm0, xmm2
    vmulps	xmm6, xmm6, xmm3
    vaddps	xmm0, xmm0, xmm4
    vaddps	xmm6, xmm6, xmm4
    vmulps	xmm0, xmm0, xmm2
    vmulps	xmm6, xmm6, xmm3
    vaddps	xmm0, xmm0, xmm5
    vaddps	xmm6, xmm6, xmm5
    vmulps	xmm0, xmm0, xmm1
    vmulps	xmm6, xmm6, xmm7

    ;vmovaps	dowrd [eax], xmm0 ; sinus(xmm0)
    ;vmovaps	dword [edx], xmm6 ; cosinus(xmm0)
    ret
    """

    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    return mc


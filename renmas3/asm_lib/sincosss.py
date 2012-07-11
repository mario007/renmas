
import renmas3.switch as proc
from tdasm import Tdasm

def sincos_ss():
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
    global fast_sincos_ss:
    movaps	xmm7, xmm0
    movss	xmm1, dword [_ps_am_inv_sign_mask]
    movss	xmm2, dword [_ps_am_sign_mask]
    movss	xmm3, dword [_ps_am_2_o_pi]
    andps	xmm0, xmm1
    andps	xmm7, xmm2
    mulss	xmm0, xmm3

    pxor	xmm3, xmm3
    movd	xmm5, dword [_epi32_1]
    movss	xmm4, dword [_ps_am_1]

    cvttps2dq	xmm2, xmm0
    pand	xmm5, xmm2
    movd	xmm1, dword [_epi32_2]
    pcmpeqd	xmm5, xmm3
    movd	xmm3, dword [_epi32_1]
    cvtdq2ps	xmm6, xmm2
    paddd	xmm3, xmm2
    pand	xmm2, xmm1
    pand	xmm3, xmm1
    subss	xmm0, xmm6
    pslld	xmm2, 30
    minss	xmm0, xmm4
    ;mov		eax, [esp + 4 + 16]
    ;mov		edx, [esp + 4 + 16 + 4]
    subss	xmm4, xmm0
    pslld	xmm3, 30

    movaps	xmm6, xmm4
    xorps	xmm2, xmm7
    movaps	xmm7, xmm5
    andps	xmm6, xmm7
    andnps	xmm7, xmm0
    andps	xmm0, xmm5
    andnps	xmm5, xmm4
    movss	xmm4, dword [_ps_sincos_p3]
    orps	xmm6, xmm7
    orps	xmm0, xmm5
    movss	xmm5, dword [_ps_sincos_p2]

    movaps	xmm1, xmm0
    movaps	xmm7, xmm6
    mulss	xmm0, xmm0
    mulss	xmm6, xmm6
    orps	xmm1, xmm2
    orps	xmm7, xmm3
    movaps	xmm2, xmm0
    movaps	xmm3, xmm6
    mulss	xmm0, xmm4
    mulss	xmm6, xmm4
    movss	xmm4, dword [_ps_sincos_p1]
    addss	xmm0, xmm5
    addss	xmm6, xmm5
    movss	xmm5, dword [_ps_sincos_p0]
    mulss	xmm0, xmm2
    mulss	xmm6, xmm3
    addss	xmm0, xmm4
    addss	xmm6, xmm4
    mulss	xmm0, xmm2
    mulss	xmm6, xmm3
    addss	xmm0, xmm5
    addss	xmm6, xmm5
    mulss	xmm0, xmm1
    mulss	xmm6, xmm7

    ;use full stores since caller might reload with full loads
    ;movaps	[eax], xmm0
    ;movaps	[edx], xmm6

    ret	
    """

    avx_code = data + """
    #CODE
    global fast_sincos_ss:
    vmovaps	xmm7, xmm0
    vmovss	xmm1, dword [_ps_am_inv_sign_mask]
    vmovss	xmm2, dword [_ps_am_sign_mask]
    vmovss	xmm3, dword [_ps_am_2_o_pi]
    vandps	xmm0, xmm0, xmm1
    vandps	xmm7, xmm7, xmm2
    vmulss	xmm0, xmm0, xmm3

    vpxor	xmm3, xmm3, xmm3
    vmovd	xmm5, dword [_epi32_1]
    vmovss	xmm4, dword [_ps_am_1]

    vcvttps2dq	xmm2, xmm0
    vpand	xmm5, xmm5, xmm2
    vmovd	xmm1, dword [_epi32_2]
    vpcmpeqd	xmm5, xmm5, xmm3
    vmovd	xmm3, dword [_epi32_1]
    vcvtdq2ps	xmm6, xmm2
    vpaddd	xmm3, xmm3, xmm2
    vpand	xmm2, xmm2, xmm1
    vpand	xmm3, xmm3, xmm1
    vsubss	xmm0, xmm0, xmm6
    vpslld	xmm2, xmm2, 30
    vminss	xmm0, xmm0, xmm4
    ;mov		eax, [esp + 4 + 16]
    ;mov		edx, [esp + 4 + 16 + 4]
    vsubss	xmm4, xmm4, xmm0
    vpslld	xmm3, xmm3, 30

    vmovaps	xmm6, xmm4
    vxorps	xmm2, xmm2, xmm7
    vmovaps	xmm7, xmm5
    vandps	xmm6, xmm6, xmm7
    vandnps	xmm7, xmm7, xmm0
    vandps	xmm0, xmm0, xmm5
    vandnps	xmm5, xmm5, xmm4
    vmovss	xmm4, dword [_ps_sincos_p3]
    vorps	xmm6, xmm6, xmm7
    vorps	xmm0, xmm0, xmm5
    vmovss	xmm5, dword [_ps_sincos_p2]

    vmovaps	xmm1, xmm0
    vmovaps	xmm7, xmm6
    vmulss	xmm0, xmm0, xmm0
    vmulss	xmm6, xmm6, xmm6
    vorps	xmm1, xmm1, xmm2
    vorps	xmm7, xmm7, xmm3
    vmovaps	xmm2, xmm0
    vmovaps	xmm3, xmm6
    vmulss	xmm0, xmm0, xmm4
    vmulss	xmm6, xmm6, xmm4
    vmovss	xmm4, dword [_ps_sincos_p1]
    vaddss	xmm0, xmm0, xmm5
    vaddss	xmm6, xmm6, xmm5
    vmovss	xmm5, dword [_ps_sincos_p0]
    vmulss	xmm0, xmm0, xmm2
    vmulss	xmm6, xmm6, xmm3
    vaddss	xmm0, xmm0, xmm4
    vaddss	xmm6, xmm6, xmm4
    vmulss	xmm0, xmm0, xmm2
    vmulss	xmm6, xmm6, xmm3
    vaddss	xmm0, xmm0, xmm5
    vaddss	xmm6, xmm6, xmm5
    vmulss	xmm0, xmm0, xmm1
    vmulss	xmm6, xmm6, xmm7

    ;use full stores since caller might reload with full loads
    ;movaps	[eax], xmm0
    ;movaps	[edx], xmm6

    ret	
    """

    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    return mc


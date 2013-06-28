
def cos_ss_asm(label, AVX=False, BIT64=True):

    global_label = "global %s:\n" % label

    data = """
    #DATA
    uint32 _ps_am_inv_sign_mask[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
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
    """
    asm_code += global_label + """
    movss	xmm1, dword [_ps_am_inv_sign_mask]
    movss	xmm2, dword [_ps_am_pi_o_2]
    movss	xmm3, dword [_ps_am_2_o_pi]
    andps	xmm0, xmm1
    addss	xmm0, xmm2
    mulss	xmm0, xmm3

    pxor	xmm3, xmm3
    movd	xmm5, dword [_epi32_1]
    movss	xmm4, dword [_ps_am_1]
    cvttps2dq	xmm2, xmm0
    pand	xmm5, xmm2
    movd	xmm1, dword [_epi32_2]
    pcmpeqd	xmm5, xmm3
    cvtdq2ps	xmm6, xmm2
    pand	xmm2, xmm1
    pslld	xmm2, 30 

    subss	xmm0, xmm6
    movss	xmm3, dword [_ps_sincos_p3]
    minss	xmm0, xmm4
    subss	xmm4, xmm0
    andps	xmm0, xmm5
    andnps	xmm5, xmm4
    orps	xmm0, xmm5

    movaps	xmm1, xmm0
    movss	xmm4, dword [_ps_sincos_p2]
    mulss	xmm0, xmm0
    movss	xmm5, dword [_ps_sincos_p1]
    orps	xmm1, xmm2
    movaps	xmm7, xmm0
    mulss	xmm0, xmm3
    movss	xmm6, dword [_ps_sincos_p0]
    addss	xmm0, xmm4
    mulss	xmm0, xmm7
    addss	xmm0, xmm5
    mulss	xmm0, xmm7
    addss	xmm0, xmm6
    mulss	xmm0, xmm1
    ret
    """

    avx_code = data + """
    #CODE
    """
    avx_code += global_label + """
    vmovss	xmm1, dword [_ps_am_inv_sign_mask]
    vmovss	xmm2, dword [_ps_am_pi_o_2]
    vmovss	xmm3, dword [_ps_am_2_o_pi]
    vandps	xmm0, xmm0, xmm1
    vaddss	xmm0, xmm0, xmm2
    vmulss	xmm0, xmm0, xmm3

    vpxor	xmm3, xmm3, xmm3
    vmovd	xmm5, dword [_epi32_1]
    vmovss	xmm4, dword [_ps_am_1]
    vcvttps2dq	xmm2, xmm0
    vpand	xmm5, xmm5, xmm2
    vmovd	xmm1, dword [_epi32_2]
    vpcmpeqd	xmm5, xmm5, xmm3
    vcvtdq2ps	xmm6, xmm2
    vpand	xmm2, xmm2, xmm1
    vpslld	xmm2, xmm2, 30 

    vsubss	xmm0, xmm0, xmm6
    vmovss	xmm3, dword [_ps_sincos_p3]
    vminss	xmm0, xmm0, xmm4
    vsubss	xmm4, xmm4, xmm0
    vandps	xmm0, xmm0, xmm5
    vandnps	xmm5, xmm5, xmm4
    vorps	xmm0, xmm0, xmm5

    vmovaps	xmm1, xmm0
    vmovss	xmm4, dword [_ps_sincos_p2]
    vmulss	xmm0, xmm0, xmm0
    vmovss	xmm5, dword [_ps_sincos_p1]
    vorps	xmm1, xmm1, xmm2
    vmovaps	xmm7, xmm0
    vmulss	xmm0, xmm0, xmm3
    vmovss	xmm6, dword [_ps_sincos_p0]
    vaddss	xmm0, xmm0, xmm4
    vmulss	xmm0, xmm0, xmm7
    vaddss	xmm0, xmm0, xmm5
    vmulss	xmm0, xmm0, xmm7
    vaddss	xmm0, xmm0, xmm6
    vmulss	xmm0, xmm0, xmm1
    ret
    """

    if AVX:
        return avx_code
    else:
        return asm_code


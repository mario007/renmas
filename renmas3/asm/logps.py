
def log_ps_asm(label, AVX=False, BIT64=True):

    global_label = "global %s:\n" % label

    data = """
    #DATA
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    uint32 _ps_am_min_norm_pos[4] = 0x00800000, 0x00800000, 0x00800000, 0x00800000
    uint32 _ps_am_inv_mant_mask[4] = 0x807FFFFF, 0x807FFFFF, 0x807FFFFF, 0x807FFFFF 
    uint32 _epi32_0x7f[4] = 0x7F, 0x7F, 0x7F, 0x7F
    float _ps_log_p0[4] = -0.789580278884, -0.789580278884, -0.789580278884, -0.789580278884
    float _ps_log_q0[4] = -35.6722798256, -35.6722798256, -35.6722798256, -35.6722798256
    float _ps_log_p1[4] = 16.38666456995, 16.38666456995, 16.38666456995, 16.38666456995
    float _ps_log_q1[4] = 312.0937663722, 312.0937663722, 312.0937663722, 312.0937663722
    float _ps_log_p2[4] = -64.14099529587, -64.14099529587, -64.14099529587, -64.14099529587
    float _ps_log_q2[4] = -769.69194355046, -769.69194355046, -769.69194355046, -769.69194355046
    float _ps_log_c0[4] = 0.6931471805599, 0.6931471805599, 0.6931471805599, 0.6931471805599 

    """
    asm_code = data + """
    #CODE
    """
    asm_code += global_label + """
    maxps	xmm0, oword [_ps_am_min_norm_pos]  ; cut off denormalized stuff
    movaps	xmm1, oword [_ps_am_1]
    movaps	xmm3, xmm0

    andps	xmm0, oword [_ps_am_inv_mant_mask]
    orps	xmm0, xmm1

    movaps	xmm4, xmm0
    subps	xmm0, xmm1
    addps	xmm4, xmm1
    psrld	xmm3, 23
    rcpps	xmm4, xmm4
    mulps	xmm0, xmm4
    psubd	xmm3, oword [_epi32_0x7f]
    addps	xmm0, xmm0

    movaps	xmm2, xmm0
    mulps	xmm0, xmm0

    movaps	xmm4, oword [_ps_log_p0]
    movaps	xmm6, oword [_ps_log_q0]

    mulps	xmm4, xmm0
    movaps	xmm5, oword [_ps_log_p1]
    mulps	xmm6, xmm0
    movaps	xmm7, oword [_ps_log_q1]

    addps	xmm4, xmm5
    addps	xmm6, xmm7

    movaps	xmm5, oword [_ps_log_p2]
    mulps	xmm4, xmm0
    movaps	xmm7, oword [_ps_log_q2]
    mulps	xmm6, xmm0

    addps	xmm4, xmm5
    movaps	xmm5, oword [_ps_log_c0]
    addps	xmm6, xmm7
    cvtdq2ps	xmm1, xmm3

    mulps	xmm0, xmm4
    rcpps	xmm6, xmm6

    mulps	xmm0, xmm6
    mulps	xmm0, xmm2

    mulps	xmm1, xmm5

    addps	xmm0, xmm2
    addps	xmm0, xmm1

    ret	


    """

    avx_code = data + """
    #CODE
    """
    avx_code += global_label + """
    vmaxps	xmm0, xmm0, oword [_ps_am_min_norm_pos]  ; cut off denormalized stuff
    vmovaps	xmm1, oword [_ps_am_1]
    vmovaps	xmm3, xmm0

    vandps	xmm0, xmm0, oword [_ps_am_inv_mant_mask]
    vorps	xmm0, xmm0, xmm1

    vmovaps	xmm4, xmm0
    vsubps	xmm0, xmm0, xmm1
    vaddps	xmm4, xmm4, xmm1
    vpsrld	xmm3, xmm3, 23
    vrcpps	xmm4, xmm4
    vmulps	xmm0, xmm0, xmm4
    vpsubd	xmm3, xmm3, oword [_epi32_0x7f]
    vaddps	xmm0, xmm0, xmm0

    vmovaps	xmm2, xmm0
    vmulps	xmm0, xmm0, xmm0

    vmovaps	xmm4, oword [_ps_log_p0]
    vmovaps	xmm6, oword [_ps_log_q0]

    vmulps	xmm4, xmm4, xmm0
    vmovaps	xmm5, oword [_ps_log_p1]
    vmulps	xmm6, xmm6, xmm0
    vmovaps	xmm7, oword [_ps_log_q1]

    vaddps	xmm4, xmm4, xmm5
    vaddps	xmm6, xmm6, xmm7

    vmovaps	xmm5, oword [_ps_log_p2]
    vmulps	xmm4, xmm4, xmm0
    vmovaps	xmm7, oword [_ps_log_q2]
    vmulps	xmm6, xmm6, xmm0

    vaddps	xmm4, xmm4, xmm5
    vmovaps	xmm5, oword [_ps_log_c0]
    vaddps	xmm6, xmm6, xmm7
    vcvtdq2ps	xmm1, xmm3

    vmulps	xmm0, xmm0, xmm4
    vrcpps	xmm6, xmm6

    vmulps	xmm0, xmm0, xmm6
    vmulps	xmm0, xmm0, xmm2

    vmulps	xmm1, xmm1, xmm5

    vaddps	xmm0, xmm0, xmm2
    vaddps	xmm0, xmm0, xmm1

    ret	


    """

    if AVX:
        return avx_code
    else:
        return asm_code



def log_ss_asm(label, AVX=False, BIT64=True):
    
    global_label = "global %s:\n" % label

    data = """
    #DATA
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    uint32 _ps_am_min_norm_pos[4] = 0x00800000, 0x00800000, 0x00800000, 0x00800000
    uint32 _ps_am_inv_mant_mask[4] = 0x807FFFFF, 0x807FFFFF, 0x807FFFFF, 0x807FFFFF 
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
    maxss	xmm0, dword [_ps_am_min_norm_pos]  ; cut off denormalized stuff
    movss	xmm1, dword [_ps_am_1]
    movd	edx, xmm0

    andps	xmm0, oword [_ps_am_inv_mant_mask]
    orps	xmm0, xmm1

    movaps	xmm4, xmm0
    subss	xmm0, xmm1
    addss	xmm4, xmm1
    shr		edx, 23
    rcpss	xmm4, xmm4
    mulss	xmm0, xmm4
    addss	xmm0, xmm0

    movaps	xmm2, xmm0
    mulss	xmm0, xmm0
    sub		edx, 0x7f

    movss	xmm4, dword [_ps_log_p0]
    movss	xmm6, dword [_ps_log_q0]

    mulss	xmm4, xmm0
    movss	xmm5, dword [_ps_log_p1]
    mulss	xmm6, xmm0
    movss	xmm7, dword [_ps_log_q1]

    addss	xmm4, xmm5
    addss	xmm6, xmm7

    movss	xmm5, dword [_ps_log_p2]
    mulss	xmm4, xmm0
    movss	xmm7, dword [_ps_log_q2]
    mulss	xmm6, xmm0

    addss	xmm4, xmm5
    movss	xmm5, dword [_ps_log_c0]
    addss	xmm6, xmm7
    cvtsi2ss	xmm1, edx

    mulss	xmm0, xmm4
    rcpss	xmm6, xmm6

    mulss	xmm0, xmm6
    mulss	xmm0, xmm2

    mulss	xmm1, xmm5

    addss	xmm0, xmm2
    addss	xmm0, xmm1

    ret	


    """

    avx_code = data + """
    #CODE
    """
    avx_code += global_label + """
    vmaxss	xmm0, xmm0, dword [_ps_am_min_norm_pos]  ; cut off denormalized stuff
    vmovss	xmm1, dword [_ps_am_1]
    vmovd	edx, xmm0

    vandps	xmm0, xmm0, oword [_ps_am_inv_mant_mask]
    vorps	xmm0, xmm0, xmm1

    vmovaps	xmm4, xmm0
    vsubss	xmm0, xmm0, xmm1
    vaddss	xmm4, xmm4, xmm1
    shr		edx, 23
    vrcpss	xmm4, xmm4, xmm4
    vmulss	xmm0, xmm0, xmm4
    vaddss	xmm0, xmm0, xmm0

    vmovaps	xmm2, xmm0
    vmulss	xmm0, xmm0, xmm0
    sub		edx, 0x7f

    vmovss	xmm4, dword [_ps_log_p0]
    vmovss	xmm6, dword [_ps_log_q0]

    vmulss	xmm4, xmm4, xmm0
    vmovss	xmm5, dword [_ps_log_p1]
    vmulss	xmm6, xmm6, xmm0
    vmovss	xmm7, dword [_ps_log_q1]

    vaddss	xmm4, xmm4, xmm5
    vaddss	xmm6, xmm6, xmm7

    vmovss	xmm5, dword [_ps_log_p2]
    vmulss	xmm4, xmm4, xmm0
    vmovss	xmm7, dword [_ps_log_q2]
    vmulss	xmm6, xmm6, xmm0

    vaddss	xmm4, xmm4, xmm5
    vmovss	xmm5, dword [_ps_log_c0]
    vaddss	xmm6, xmm6, xmm7
    vcvtsi2ss	xmm1, xmm1, edx

    vmulss	xmm0, xmm0, xmm4
    vrcpss	xmm6, xmm6, xmm6

    vmulss	xmm0, xmm0, xmm6
    vmulss	xmm0, xmm0, xmm2

    vmulss	xmm1, xmm1, xmm5

    vaddss	xmm0, xmm0, xmm2
    vaddss	xmm0, xmm0, xmm1

    ret	


    """

    if AVX:
        return avx_code
    else:
        return asm_code


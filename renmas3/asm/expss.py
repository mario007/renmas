
def exp_ss_asm(label, AVX=False, BIT64=True):

    global_label = "global %s:\n" % label

    data = """
    #DATA
    float _ps_exp_hi[4] = 88.37626266479, 88.37626266479, 88.37626266479, 88.37626266479
    float _ps_exp_rln2[4] = 1.44269504088896, 1.44269504088896, 1.44269504088896, 1.44269504088896
    float _ps_exp_lo[4] = -88.37626266479, -88.37626266479, -88.37626266479, -88.37626266479
    float _ps_am_0p5[4] = 0.5, 0.5, 0.5, 0.5
    uint32 _epi32_1[4] = 1, 1, 1, 1

    float _ps_exp_c2[4] = 0.0000014286068203, 0.0000014286068203, 0.0000014286068203, 0.0000014286068203
    float _ps_exp_c1[4] = 0.693145751953125, 0.693145751953125, 0.693145751953125, 0.693145751953125
    float _ps_exp_q0[4] = 0.00000300198505138664, 0.00000300198505138664, 0.00000300198505138664, 0.00000300198505138664
    float _ps_exp_p0[4] = 0.0001261771930748, 0.0001261771930748, 0.0001261771930748, 0.0001261771930748
    uint32 _epi32_0x7f[4] = 0x7F, 0x7F, 0x7F, 0x7F
    float _ps_exp_q1[4] = 0.002524483403497, 0.002524483403497, 0.002524483403497, 0.002524483403497
    float _ps_exp_p1[4] = 0.03029944077074, 0.03029944077074, 0.03029944077074, 0.03029944077074
    float _ps_exp_q2[4] = 0.227265548208156, 0.227265548208156, 0.227265548208156, 0.227265548208156
    float _ps_exp_q3[4] = 2.0, 2.0, 2.0, 2.0
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0

    """

    asm_code = data + """
    #CODE
    """
    asm_code += global_label + """
    minss	xmm0, dword [_ps_exp_hi]
    movss	xmm1, dword [_ps_exp_rln2]
    maxss	xmm0, dword [_ps_exp_lo]
    mulss	xmm1, xmm0
    movd	xmm3, dword [_epi32_1]
    xorps	xmm2, xmm2
    addss	xmm1, dword [_ps_am_0p5]

    cmpss	xmm2, xmm1, 5
    pand	xmm2, xmm3

    cvttps2dq	xmm1, xmm1
    movss	xmm4, dword [_ps_exp_c2]

    psubd	xmm1, xmm2
    movss	xmm5, dword [_ps_exp_c1]

    cvtdq2ps	xmm3, xmm1

    movd	xmm7, dword [_epi32_0x7f]

    mulss	xmm4, xmm3
    mulss	xmm5, xmm3
    movss	xmm6, dword [_ps_exp_q0]
    subss	xmm0, xmm4
    movss	xmm4, dword [_ps_exp_p0]
    subss	xmm0, xmm5

    paddd	xmm1, xmm7
    movss	xmm2, xmm0
    mulss	xmm0, xmm0

    movss	xmm5, dword [_ps_exp_q1]
    mulss	xmm6, xmm0
    movss	xmm3, dword [_ps_exp_p1]
    mulss	xmm4, xmm0
    addss	xmm6, xmm5
    movss	xmm5, dword [_ps_exp_q2]
    addss	xmm4, xmm3
    movss	xmm3, dword [_ps_exp_q3]
    mulss	xmm6, xmm0
    mulss	xmm4, xmm0
    addss	xmm6, xmm5
    mulss	xmm4, xmm2
    mulss	xmm6, xmm0
    movss	xmm0, dword [_ps_am_1]
    addss	xmm2, xmm4
    addss	xmm6, xmm3

    pslld	xmm1, 23
    subss	xmm6, xmm2
    rcpss	xmm6, xmm6
    mulss	xmm2, xmm6
    addss	xmm2, xmm2
    addss	xmm0, xmm2

    mulss	xmm0, xmm1

    ret
    """

    avx_code = data + """
    #CODE
    """
    avx_code += global_label + """
    vminss	xmm0, xmm0, dword [_ps_exp_hi]
    vmovss	xmm1, dword [_ps_exp_rln2]
    vmaxss	xmm0, xmm0, dword [_ps_exp_lo]
    vmulss	xmm1, xmm1, xmm0
    vmovd	xmm3, dword [_epi32_1]
    vxorps	xmm2, xmm2, xmm2
    vaddss	xmm1, xmm1, dword [_ps_am_0p5]

    vcmpss	xmm2, xmm2, xmm1, 5
    vpand	xmm2, xmm2, xmm3

    vcvttps2dq	xmm1, xmm1
    vmovss	xmm4, dword [_ps_exp_c2]

    vpsubd	xmm1, xmm1, xmm2
    vmovss	xmm5, dword [_ps_exp_c1]

    vcvtdq2ps	xmm3, xmm1

    vmovd	xmm7, dword [_epi32_0x7f]

    vmulss	xmm4, xmm4, xmm3
    vmulss	xmm5, xmm5, xmm3
    vmovss	xmm6, dword [_ps_exp_q0]
    vsubss	xmm0, xmm0, xmm4
    vmovss	xmm4, dword [_ps_exp_p0]
    vsubss	xmm0, xmm0, xmm5

    vpaddd	xmm1, xmm1, xmm7
    vmovss	xmm2, xmm2, xmm0
    vmulss	xmm0, xmm0, xmm0

    vmovss	xmm5, dword [_ps_exp_q1]
    vmulss	xmm6, xmm6, xmm0
    vmovss	xmm3, dword [_ps_exp_p1]
    vmulss	xmm4, xmm4, xmm0
    vaddss	xmm6, xmm6, xmm5
    vmovss	xmm5, dword [_ps_exp_q2]
    vaddss	xmm4, xmm4, xmm3
    vmovss	xmm3, dword [_ps_exp_q3]
    vmulss	xmm6, xmm6, xmm0
    vmulss	xmm4, xmm4, xmm0
    vaddss	xmm6, xmm6, xmm5
    vmulss	xmm4, xmm4, xmm2
    vmulss	xmm6, xmm6, xmm0
    vmovss	xmm0, dword [_ps_am_1]
    vaddss	xmm2, xmm2, xmm4
    vaddss	xmm6, xmm6, xmm3

    vpslld	xmm1, xmm1, 23
    vsubss	xmm6, xmm6, xmm2
    vrcpss	xmm6, xmm6, xmm6
    vmulss	xmm2, xmm2, xmm6
    vaddss	xmm2, xmm2, xmm2
    vaddss	xmm0, xmm0, xmm2

    vmulss	xmm0, xmm0, xmm1

    ret
    """

    if AVX:
        return avx_code
    else:
        return asm_code


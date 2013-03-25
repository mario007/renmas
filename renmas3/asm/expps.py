
def exp_ps_asm(label, AVX=False, BIT64=True):

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
    minps	xmm0, oword [_ps_exp_hi]
    movaps	xmm1, oword [_ps_exp_rln2]
    maxps	xmm0, oword [_ps_exp_lo]
    mulps	xmm1, xmm0
    xorps	xmm2, xmm2
    addps	xmm1, oword [_ps_am_0p5]

    cmpps	xmm2, xmm1, 5
    pand	xmm2, oword [_epi32_1]

    cvttps2dq	xmm1, xmm1
    movaps	xmm4, oword [_ps_exp_c2]

    psubd	xmm1, xmm2
    movaps	xmm5, oword [_ps_exp_c1]

    cvtdq2ps	xmm3, xmm1

    mulps	xmm4, xmm3
    mulps	xmm5, xmm3
    movaps	xmm6, oword [_ps_exp_q0]
    subps	xmm0, xmm4
    movaps	xmm4, oword [_ps_exp_p0]
    subps	xmm0, xmm5

    paddd	xmm1, oword [_epi32_0x7f]
    movaps	xmm2, xmm0
    mulps	xmm0, xmm0

    movaps	xmm5, oword [_ps_exp_q1]
    mulps	xmm6, xmm0
    movaps	xmm3, oword [_ps_exp_p1]
    mulps	xmm4, xmm0
    addps	xmm6, xmm5
    movaps	xmm5, oword [_ps_exp_q2]
    addps	xmm4, xmm3
    movaps	xmm3, oword [_ps_exp_q3]
    mulps	xmm6, xmm0
    mulps	xmm4, xmm0
    addps	xmm6, xmm5
    mulps	xmm4, xmm2
    mulps	xmm6, xmm0
    movaps	xmm0, oword [_ps_am_1]
    addps	xmm2, xmm4
    addps	xmm6, xmm3

    pslld	xmm1, 23
    subps	xmm6, xmm2
    rcpps	xmm6, xmm6
    mulps	xmm2, xmm6
    addps	xmm2, xmm2
    addps	xmm0, xmm2

    mulps	xmm0, xmm1

    ret	
    """

    avx_code = data + """
    #CODE
    """
    avx_code += global_label + """ 
    vminps	xmm0, xmm0, oword [_ps_exp_hi]
    vmovaps	xmm1, oword [_ps_exp_rln2]
    vmaxps	xmm0, xmm0, oword [_ps_exp_lo]
    vmulps	xmm1, xmm1, xmm0
    vxorps	xmm2, xmm2, xmm2
    vaddps	xmm1, xmm1, oword [_ps_am_0p5]

    vcmpps	xmm2, xmm2, xmm1, 5
    vpand	xmm2, xmm2, oword [_epi32_1]

    vcvttps2dq	xmm1, xmm1
    vmovaps	xmm4, oword [_ps_exp_c2]

    vpsubd	xmm1, xmm1, xmm2
    vmovaps	xmm5, oword [_ps_exp_c1]

    vcvtdq2ps	xmm3, xmm1

    vmulps	xmm4, xmm4, xmm3
    vmulps	xmm5, xmm5, xmm3
    vmovaps	xmm6, oword [_ps_exp_q0]
    vsubps	xmm0, xmm0, xmm4
    vmovaps	xmm4, oword [_ps_exp_p0]
    vsubps	xmm0, xmm0, xmm5

    vpaddd	xmm1, xmm1, oword [_epi32_0x7f]
    vmovaps	xmm2, xmm0
    vmulps	xmm0, xmm0, xmm0

    vmovaps	xmm5, oword [_ps_exp_q1]
    vmulps	xmm6, xmm6, xmm0
    vmovaps	xmm3, oword [_ps_exp_p1]
    vmulps	xmm4, xmm4, xmm0
    vaddps	xmm6, xmm6, xmm5
    vmovaps	xmm5, oword [_ps_exp_q2]
    vaddps	xmm4, xmm4, xmm3
    vmovaps	xmm3, oword [_ps_exp_q3]
    vmulps	xmm6, xmm6, xmm0
    vmulps	xmm4, xmm4, xmm0
    vaddps	xmm6, xmm6, xmm5
    vmulps	xmm4, xmm4, xmm2
    vmulps	xmm6, xmm6, xmm0
    vmovaps	xmm0, oword [_ps_am_1]
    vaddps	xmm2, xmm2, xmm4
    vaddps	xmm6, xmm6, xmm3

    vpslld	xmm1, xmm1, 23
    vsubps	xmm6, xmm6, xmm2
    vrcpps	xmm6, xmm6
    vmulps	xmm2, xmm2, xmm6
    vaddps	xmm2, xmm2, xmm2
    vaddps	xmm0, xmm0, xmm2

    vmulps	xmm0, xmm0, xmm1

    ret	
    """

    if AVX:
        return avx_code
    else:
        return asm_code


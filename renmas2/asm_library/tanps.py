
import renmas2.switch as proc
from tdasm import Tdasm

def tan_ps():
    data = """
    #DATA
    uint32 _ps_am_inv_sign_mask[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
    float _ps_am_4_o_pi[4] = 1.273239544735, 1.273239544735, 1.273239544735, 1.273239544735
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_am_pi_o_4[4] = 0.78539816339, 0.78539816339, 0.78539816339, 0.78539816339
    int32 _epi32_1[4] = 1, 1, 1, 1
    int32 _epi32_7[4] = 7, 7, 7, 7
    int32 _epi32_2[4] = 2, 2, 2, 2
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_tan_p0[4] = -17956525.197648, -17956525.197648, -17956525.197648, -17956525.197648 
    float _ps_tan_q0[4] = -53869575.592945, -53869575.592945, -53869575.592945, -53869575.592945 
    float _ps_tan_p1[4] = 1153516.64838587, 1153516.64838587, 1153516.64838587, 1153516.64838587
    float _ps_tan_q1[4] = 25008380.18233579, 25008380.18233579, 25008380.18233579, 25008380.18233579
    float _ps_tan_p2[4] = -13093.693918138, -13093.693918138, -13093.693918138, -13093.693918138
    float _ps_tan_q2[4] = -1320892.3444021, -1320892.3444021, -1320892.3444021, -1320892.3444021
    float _ps_tan_q3[4] = 13681.296347069, 13681.296347069, 13681.296347069, 13681.296347069
    float _ps_tan_poleval[4] = 36893500000000000000.0, 36893500000000000000.0, 36893500000000000000.0, 36893500000000000000.0

    """
    asm_code = data + """

    #CODE
    global fast_tan_ps:
    movaps	xmm7, xmm0
    andps	xmm0, oword [_ps_am_inv_sign_mask]
    andps	xmm7, oword [_ps_am_sign_mask]
    movaps	xmm1, xmm0
    mulps	xmm0, oword [_ps_am_4_o_pi]

    cvttps2dq	xmm0, xmm0
    movdqa	xmm4, oword [_epi32_1]
    movdqa	xmm5, oword [_epi32_7]

    pand	xmm4, xmm0
    pand	xmm5, xmm0
    movaps	xmm3, oword [_ps_am_1]
    paddd	xmm0, xmm4
    paddd	xmm5, xmm4

    cvtdq2ps	xmm0, xmm0

    mulps	xmm0, oword [_ps_am_pi_o_4]
    xorps	xmm6, xmm6
    subps	xmm1, xmm0
    movaps	xmm2, oword [_ps_tan_p2]
    minps	xmm1, xmm3
    movaps	xmm3, oword [_ps_tan_q3]
    movaps	xmm0, xmm1
    mulps	xmm1, xmm1

    mulps	xmm2, xmm1
    addps	xmm3, xmm1
    addps	xmm2, oword [_ps_tan_p1]
    mulps	xmm3, xmm1
    mulps	xmm2, xmm1
    addps	xmm3, oword [_ps_tan_q2]
    addps	xmm2, oword [_ps_tan_p0]
    mulps	xmm3, xmm1
    mulps	xmm2, xmm1
    addps	xmm3, oword [_ps_tan_q1]
    xorps	xmm0, xmm7
    mulps	xmm3, xmm1
    pand	xmm5, oword [_epi32_2]
    addps	xmm3, oword [_ps_tan_q0]
    mulps	xmm2, xmm0

    cmpps xmm6, xmm1, 4
    rcpps	xmm4, xmm3
    pxor	xmm7, xmm7
    mulps	xmm3, xmm4
    pcmpeqd	xmm5, xmm7
    mulps	xmm3, xmm4
    addps	xmm4, xmm4
    orps	xmm6, xmm5
    subps	xmm4, xmm3

    mulps	xmm2, xmm4
    movaps	xmm1, oword [_ps_am_sign_mask]
    movmskps	eax, xmm6
    addps	xmm2, xmm0

    rcpps	xmm4, xmm2
    cmp		eax, 0xf
    movaps	xmm0, xmm2
    mulps	xmm2, xmm4
    mulps	xmm2, xmm4
    addps	xmm4, xmm4
    subps	xmm4, xmm2
    jne		l_pole

    xorps	xmm4, xmm1

    andps	xmm0, xmm5
    andnps	xmm5, xmm4
    orps	xmm0, xmm5

    ret	

    l_pole:
    movaps	xmm7, xmm1
    movaps	xmm3, oword [_ps_tan_poleval]
    andps	xmm1, xmm0
    orps	xmm3, xmm1
    andps	xmm4, xmm6
    andnps	xmm6, xmm3
    orps	xmm4, xmm6

    xorps	xmm4, xmm7

    andps	xmm0, xmm5
    andnps	xmm5, xmm4
    orps	xmm0, xmm5

    ret	


    """

    avx_code = data + """

    #CODE
    global fast_tan_ps:
    vmovaps	xmm7, xmm0
    vandps	xmm0, xmm0, oword [_ps_am_inv_sign_mask]
    vandps	xmm7, xmm7, oword [_ps_am_sign_mask]
    vmovaps	xmm1, xmm0
    vmulps	xmm0, xmm0, oword [_ps_am_4_o_pi]

    vcvttps2dq	xmm0, xmm0
    vmovdqa	xmm4, oword [_epi32_1]
    vmovdqa	xmm5, oword [_epi32_7]

    vpand	xmm4, xmm4, xmm0
    vpand	xmm5, xmm5, xmm0
    vmovaps	xmm3, oword [_ps_am_1]
    vpaddd	xmm0, xmm0, xmm4
    vpaddd	xmm5, xmm5, xmm4

    vcvtdq2ps	xmm0, xmm0

    vmulps	xmm0, xmm0, oword [_ps_am_pi_o_4]
    vxorps	xmm6, xmm6, xmm6
    vsubps	xmm1, xmm1, xmm0
    vmovaps	xmm2, oword [_ps_tan_p2]
    vminps	xmm1, xmm1, xmm3
    vmovaps	xmm3, oword [_ps_tan_q3]
    vmovaps	xmm0, xmm1
    vmulps	xmm1, xmm1, xmm1

    vmulps	xmm2, xmm2, xmm1
    vaddps	xmm3, xmm3, xmm1
    vaddps	xmm2, xmm2, oword [_ps_tan_p1]
    vmulps	xmm3, xmm3, xmm1
    vmulps	xmm2, xmm2, xmm1
    vaddps	xmm3, xmm3, oword [_ps_tan_q2]
    vaddps	xmm2, xmm2, oword [_ps_tan_p0]
    vmulps	xmm3, xmm3, xmm1
    vmulps	xmm2, xmm2, xmm1
    vaddps	xmm3, xmm3, oword [_ps_tan_q1]
    vxorps	xmm0, xmm0, xmm7
    vmulps	xmm3, xmm3, xmm1
    vpand	xmm5, xmm5, oword [_epi32_2]
    vaddps	xmm3, xmm3, oword [_ps_tan_q0]
    vmulps	xmm2, xmm2, xmm0

    vcmpps xmm6, xmm6, xmm1, 4
    vrcpps	xmm4, xmm3
    vpxor	xmm7, xmm7, xmm7
    vmulps	xmm3, xmm3, xmm4
    vpcmpeqd	xmm5, xmm5, xmm7
    vmulps	xmm3, xmm3, xmm4
    vaddps	xmm4, xmm4, xmm4
    vorps	xmm6, xmm6, xmm5
    vsubps	xmm4, xmm4, xmm3

    vmulps	xmm2, xmm2, xmm4
    vmovaps	xmm1, oword [_ps_am_sign_mask]
    vmovmskps	eax, xmm6
    vaddps	xmm2, xmm2, xmm0

    vrcpps	xmm4, xmm2
    cmp		eax, 0xf
    vmovaps	xmm0, xmm2
    vmulps	xmm2, xmm2, xmm4
    vmulps	xmm2, xmm2, xmm4
    vaddps	xmm4, xmm4, xmm4
    vsubps	xmm4, xmm4, xmm2
    jne		l_pole

    vxorps	xmm4, xmm4, xmm1

    vandps	xmm0, xmm0, xmm5
    vandnps	xmm5, xmm5, xmm4
    vorps	xmm0, xmm0, xmm5

    ret	

    l_pole:
    vmovaps	xmm7, xmm1
    vmovaps	xmm3, oword [_ps_tan_poleval]
    vandps	xmm1, xmm1, xmm0
    vorps	xmm3, xmm3, xmm1
    vandps	xmm4, xmm4, xmm6
    vandnps	xmm6, xmm6, xmm3
    vorps	xmm4, xmm4, xmm6

    vxorps	xmm4, xmm4, xmm7

    vandps	xmm0, xmm0, xmm5
    vandnps	xmm5, xmm5, xmm4
    vorps	xmm0, xmm0, xmm5

    ret	


    """

    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    return mc

    #name = "fast_tan_ps"  
    #runtime.load(name, mc)


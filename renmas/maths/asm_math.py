
"""
Assembly module for approximations of transcendental functions. Thease approximations are used from 
Intel approximations library.

"""

from tdasm import Tdasm
import renmas.utils as util

def exp_ss(runtime):
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
    global fast_exp_ss:
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
    global fast_exp_ss:
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

    asm = Tdasm()
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_exp_ss"  
    runtime.load(name, mc)

def exp_ps(runtime):
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
    global fast_exp_ps:
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
    global fast_exp_ps:
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

    asm = Tdasm()
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_exp_ps"  
    runtime.load(name, mc)
    

def sincos_ss(runtime):
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
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_sincos_ss"  
    runtime.load(name, mc)


def sincos_ps(runtime):
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
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_sincos_ps"  
    runtime.load(name, mc)


def cos_ss(runtime):
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
    global fast_cos_ss:
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
    global fast_cos_ss:
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

    asm = Tdasm()
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    name = "fast_cos_ss"  
    runtime.load(name, mc)


def cos_ps(runtime):
   
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
    global fast_cos_ps:
    andps	xmm0, oword [_ps_am_inv_sign_mask]
    addps	xmm0, oword [_ps_am_pi_o_2]
    mulps	xmm0, oword [_ps_am_2_o_pi]

    pxor	xmm3, xmm3
    movdqa	xmm5, oword [_epi32_1]
    movaps	xmm4, oword [_ps_am_1]
    cvttps2dq	xmm2, xmm0
    pand	xmm5, xmm2
    pcmpeqd	xmm5, xmm3
    cvtdq2ps	xmm6, xmm2
    pand	xmm2, oword [_epi32_2]
    pslld	xmm2, 30 

    subps	xmm0, xmm6
    minps	xmm0, xmm4
    subps	xmm4, xmm0
    andps	xmm0, xmm5
    andnps	xmm5, xmm4
    orps	xmm0, xmm5

    movaps	xmm1, xmm0
    mulps	xmm0, xmm0
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
    global fast_cos_ps:
    vandps	xmm0, xmm0, oword [_ps_am_inv_sign_mask]
    vaddps	xmm0, xmm0, oword [_ps_am_pi_o_2]
    vmulps	xmm0, xmm0, oword [_ps_am_2_o_pi]

    vpxor	xmm3, xmm3, xmm3
    vmovdqa	xmm5, oword [_epi32_1]
    vmovaps	xmm4, oword [_ps_am_1]
    vcvttps2dq	xmm2, xmm0
    vpand	xmm5, xmm5, xmm2
    vpcmpeqd	xmm5, xmm5, xmm3
    vcvtdq2ps	xmm6, xmm2
    vpand	xmm2, xmm2, oword [_epi32_2]
    vpslld	xmm2, xmm2, 30 

    vsubps	xmm0, xmm0, xmm6
    vminps	xmm0, xmm0, xmm4
    vsubps	xmm4, xmm4, xmm0
    vandps	xmm0, xmm0, xmm5
    vandnps	xmm5, xmm5, xmm4
    vorps	xmm0, xmm0, xmm5

    vmovaps	xmm1, xmm0
    vmulps	xmm0, xmm0, xmm0
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
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    name = "fast_cos_ps"  
    runtime.load(name, mc)

def sin_ss(runtime):
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
    global fast_sin_ss:
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
	xorps	xmm2, xmm7
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
    global fast_sin_ss:
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
	vxorps	xmm2, xmm2, xmm7
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

    asm = Tdasm()
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    name = "fast_sin_ss"  
    runtime.load(name, mc)
    

def sin_ps(runtime):
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
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_sin_ps"  
    runtime.load(name, mc)

def pow_ss(runtime):
    data = """
    #DATA

    uint32 _epi32_1[4] = 1, 1, 1, 1
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0

    uint32 _ps_am_inv_mant_mask[4] = 0x807FFFFF,  0x807FFFFF,  0x807FFFFF,  0x807FFFFF 
    uint32 _ps_am_min_norm_pos[4] = 0x00800000, 0x00800000, 0x00800000, 0x00800000
    uint32 _epi32_0x7f[4] = 0x7F, 0x7F, 0x7F, 0x7F

    float _ps_log_p0[4] = -0.7895802788, -0.7895802788, -0.7895802788, -0.7895802788
    float _ps_log_q0[4] = -35.6722798256, -35.6722798256, -35.6722798256, -35.6722798256
    float _ps_log_p1[4] = 16.3866645699,  16.3866645699,  16.3866645699,  16.3866645699
    float _ps_log_q1[4] = 312.093766372,  312.093766372,  312.093766372,  312.093766372
    float _ps_log_p2[4] = -64.14099529,  -64.14099529,  -64.14099529,  -64.14099529
    float _ps_log_q2[4] = -769.691943550,  -769.691943550,  -769.691943550,  -769.691943550

    float _ps_log2_c0[4] = 1.442695040,  1.442695040,  1.442695040,  1.442695040
    float _ps_exp2_hi[4] = 127.4999961,  127.4999961,  127.4999961,  127.4999961
    float _ps_exp2_lo[4] = -127.4999961,  -127.4999961,  -127.4999961,  -127.4999961
    float _ps_am_0p5[4] = 0.5, 0.5, 0.5, 0.5
    float _ps_exp2_p0[4] = 0.0230933477, 0.0230933477, 0.0230933477, 0.0230933477
    float _ps_exp2_q0[4] = 233.18421172, 233.18421172, 233.18421172, 233.18421172 
    float _ps_exp2_p1[4] = 20.202065669,  20.202065669,  20.202065669,  20.202065669
    float _ps_exp2_q1[4] = 4368.211668, 4368.211668, 4368.211668, 4368.211668
    float _ps_exp2_p2[4] = 1513.90680, 1513.90680, 1513.90680, 1513.90680
    """
    asm_code = data + """

    #CODE
    global fast_pow_ss:
	xorps	xmm5, xmm5
	movss	xmm2, dword [_ps_am_inv_mant_mask]
	cmpss   xmm5, xmm0, 1
	maxss	xmm0, dword [_ps_am_min_norm_pos]  ;// cut off denormalized stuff
	movss	xmm7, dword [_ps_am_1]
	movaps	xmm3, xmm0

	andps	xmm0, xmm2
	orps	xmm0, xmm7

	movss	dword [esp - 4], xmm5

	movaps	xmm4, xmm0
	movd	xmm2, dword [_epi32_0x7f]
	subss	xmm0, xmm7
	addss	xmm4, xmm7
	psrld	xmm3, 23
	rcpss	xmm4, xmm4
	mulss	xmm0, xmm4
	psubd	xmm3, xmm2
	addss	xmm0, xmm0

	movaps	xmm2, xmm0
	mulss	xmm0, xmm0

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
	movss	xmm5, dword [_ps_log2_c0]
	addss	xmm6, xmm7
	cvtdq2ps	xmm7, xmm3

	mulss	xmm0, xmm4
	rcpss	xmm6, xmm6

	mulss	xmm0, xmm6
	movss	xmm4, dword [_ps_exp2_hi]
	mulss	xmm0, xmm2
	movss	xmm6, dword [_ps_exp2_lo]
	mulss	xmm2, xmm5
	mulss	xmm0, xmm5
	addss	xmm2, xmm7
	movss	xmm3, dword [_ps_am_0p5]
	addss	xmm0, xmm2
	xorps	xmm2, xmm2
	movd	xmm5, dword [_epi32_1]

	mulss	xmm0, xmm1

	minss	xmm0, xmm4
	movss	xmm4, dword [_ps_exp2_p0]
	maxss	xmm0, xmm6
	movss	xmm6, dword [_ps_exp2_q0]

	addss	xmm3, xmm0

	cmpss xmm2, xmm3, 5
	pand	xmm2, xmm5

	cvttps2dq	xmm3, xmm3

	psubd	xmm3, xmm2

	cvtdq2ps	xmm2, xmm3

	subss	xmm0, xmm2

	movaps	xmm2, xmm0
	mulss	xmm0, xmm0

	paddd	xmm3, oword [_epi32_0x7f]

	mulss	xmm4, xmm0
	mulss	xmm6, xmm0
	addss	xmm4, dword [_ps_exp2_p1]
	addss	xmm6, dword [_ps_exp2_q1]

	mulss	xmm4, xmm0
	addss	xmm4, dword [_ps_exp2_p2]

	mulss	xmm2, xmm4

	movss	xmm0, dword [_ps_am_1]
	subss	xmm6, xmm2
	pslld	xmm3, 23
	rcpss	xmm6, xmm6
	movss	xmm5, dword [esp - 4]
	mulss	xmm2, xmm6
	andps	xmm3, xmm5
	addss	xmm2, xmm2
	addss	xmm0, xmm2

	mulss	xmm0, xmm3
    ret
    """

    avx_code = data + """

    #CODE
    global fast_pow_ss:
	vxorps	xmm5, xmm5, xmm5
	vmovss	xmm2, dword [_ps_am_inv_mant_mask]
	vcmpss  xmm5, xmm5, xmm0, 1
	vmaxss	xmm0, xmm0, dword [_ps_am_min_norm_pos]  ;// cut off denormalized stuff
	vmovss	xmm7, dword [_ps_am_1]
	vmovaps	xmm3, xmm0

	vandps	xmm0, xmm0, xmm2
	vorps	xmm0, xmm0, xmm7

	vmovss	dword [esp - 4], xmm5

	vmovaps	xmm4, xmm0
	vmovd	xmm2, dword [_epi32_0x7f]
	vsubss	xmm0, xmm0, xmm7
	vaddss	xmm4, xmm4, xmm7
	vpsrld	xmm3, xmm3, 23
	vrcpss	xmm4, xmm4, xmm4
	vmulss	xmm0, xmm0, xmm4
	vpsubd	xmm3, xmm3, xmm2
	vaddss	xmm0, xmm0, xmm0

	vmovaps	xmm2, xmm0
	vmulss	xmm0, xmm0, xmm0

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
	vmovss	xmm5, dword [_ps_log2_c0]
	vaddss	xmm6, xmm6, xmm7
	vcvtdq2ps	xmm7, xmm3

	vmulss	xmm0, xmm0, xmm4
	vrcpss	xmm6, xmm6, xmm6

	vmulss	xmm0, xmm0, xmm6
	vmovss	xmm4, dword [_ps_exp2_hi]
	vmulss	xmm0, xmm0, xmm2
	vmovss	xmm6, dword [_ps_exp2_lo]
	vmulss	xmm2, xmm2, xmm5
	vmulss	xmm0, xmm0, xmm5
	vaddss	xmm2, xmm2, xmm7
	vmovss	xmm3, dword [_ps_am_0p5]
	vaddss	xmm0, xmm0, xmm2
	vxorps	xmm2, xmm2, xmm2
	vmovd	xmm5, dword [_epi32_1]

	vmulss	xmm0, xmm0, xmm1

	vminss	xmm0, xmm0, xmm4
	vmovss	xmm4, dword [_ps_exp2_p0]
	vmaxss	xmm0, xmm0, xmm6
	vmovss	xmm6, dword [_ps_exp2_q0]

	vaddss	xmm3, xmm3, xmm0

	vcmpss xmm2, xmm2, xmm3, 5
	vpand	xmm2, xmm2, xmm5

	vcvttps2dq	xmm3, xmm3

	vpsubd	xmm3, xmm3, xmm2

	vcvtdq2ps	xmm2, xmm3

	vsubss	xmm0, xmm0, xmm2

	vmovaps	xmm2, xmm0
	vmulss	xmm0, xmm0, xmm0

	vpaddd	xmm3, xmm3, oword [_epi32_0x7f]

	vmulss	xmm4, xmm4, xmm0
	vmulss	xmm6, xmm6, xmm0
	vaddss	xmm4, xmm4, dword [_ps_exp2_p1]
	vaddss	xmm6, xmm6, dword [_ps_exp2_q1]

	vmulss	xmm4, xmm4, xmm0
	vaddss	xmm4, xmm4, dword [_ps_exp2_p2]

	vmulss	xmm2, xmm2, xmm4

	vmovss	xmm0, dword [_ps_am_1]
	vsubss	xmm6, xmm6, xmm2
	vpslld	xmm3, xmm3, 23
	vrcpss	xmm6, xmm6, xmm6
	vmovss	xmm5, dword [esp - 4]
	vmulss	xmm2, xmm2, xmm6
	vandps	xmm3, xmm3, xmm5
	vaddss	xmm2, xmm2, xmm2
	vaddss	xmm0, xmm0, xmm2

	vmulss	xmm0, xmm0, xmm3
    ret
    """

    asm = Tdasm()
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_pow_ss"  
    runtime.load(name, mc)


def pow_ps(runtime):
    data = """
    #DATA

    uint32 _epi32_1[4] = 1, 1, 1, 1
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0

    uint32 _ps_am_inv_mant_mask[4] = 0x807FFFFF,  0x807FFFFF,  0x807FFFFF,  0x807FFFFF 
    uint32 _ps_am_min_norm_pos[4] = 0x00800000, 0x00800000, 0x00800000, 0x00800000
    uint32 _epi32_0x7f[4] = 0x7F, 0x7F, 0x7F, 0x7F

    float _ps_log_p0[4] = -0.7895802788, -0.7895802788, -0.7895802788, -0.7895802788
    float _ps_log_q0[4] = -35.6722798256, -35.6722798256, -35.6722798256, -35.6722798256
    float _ps_log_p1[4] = 16.3866645699,  16.3866645699,  16.3866645699,  16.3866645699
    float _ps_log_q1[4] = 312.093766372,  312.093766372,  312.093766372,  312.093766372
    float _ps_log_p2[4] = -64.14099529,  -64.14099529,  -64.14099529,  -64.14099529
    float _ps_log_q2[4] = -769.691943550,  -769.691943550,  -769.691943550,  -769.691943550

    float _ps_log2_c0[4] = 1.442695040,  1.442695040,  1.442695040,  1.442695040
    float _ps_exp2_hi[4] = 127.4999961,  127.4999961,  127.4999961,  127.4999961
    float _ps_exp2_lo[4] = -127.4999961,  -127.4999961,  -127.4999961,  -127.4999961
    float _ps_am_0p5[4] = 0.5, 0.5, 0.5, 0.5
    float _ps_exp2_p0[4] = 0.0230933477, 0.0230933477, 0.0230933477, 0.0230933477
    float _ps_exp2_q0[4] = 233.18421172, 233.18421172, 233.18421172, 233.18421172 
    float _ps_exp2_p1[4] = 20.202065669,  20.202065669,  20.202065669,  20.202065669
    float _ps_exp2_q1[4] = 4368.211668, 4368.211668, 4368.211668, 4368.211668
    float _ps_exp2_p2[4] = 1513.90680, 1513.90680, 1513.90680, 1513.90680

    """
    asm_code = data + """

    #CODE
    global fast_pow_ps:
	xorps	xmm5, xmm5
	cmpps xmm5, xmm0, 1
	mov	eax , esp
	maxps	xmm0, oword [ _ps_am_min_norm_pos]  ;// cut off denormalized stuff
	movaps	xmm7, oword [_ps_am_1]
	movaps	xmm3, xmm0
	and 	eax, 0xFFFFFFF0

	andps	xmm0, oword [_ps_am_inv_mant_mask]
	orps	xmm0, xmm7

	movaps	oword [eax - 16], xmm5

	movaps	xmm4, xmm0
	subps	xmm0, xmm7
	addps	xmm4, xmm7
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
	movaps	xmm5, oword [_ps_log2_c0]
	addps	xmm6, xmm7
	cvtdq2ps	xmm7, xmm3

	mulps	xmm0, xmm4
	rcpps	xmm6, xmm6

	mulps	xmm0, xmm6
	movaps	xmm4, oword [_ps_exp2_hi]
	mulps	xmm0, xmm2
	movaps	xmm6, oword [_ps_exp2_lo]
	mulps	xmm2, xmm5
	mulps	xmm0, xmm5
	addps	xmm2, xmm7
	movaps	xmm3, oword [_ps_am_0p5]
	addps	xmm0, xmm2
	xorps	xmm2, xmm2

	mulps	xmm0, xmm1

	minps	xmm0, xmm4
	movaps	xmm4, oword [_ps_exp2_p0]
	maxps	xmm0, xmm6
	movaps	xmm6, oword [_ps_exp2_q0]

	addps	xmm3, xmm0

	cmpps xmm2, xmm3, 5
	pand	xmm2, oword [_epi32_1]

	cvttps2dq	xmm3, xmm3

	psubd	xmm3, xmm2
	movaps	xmm5, oword [_ps_exp2_p1]

	cvtdq2ps	xmm2, xmm3
	movaps	xmm7, oword [_ps_exp2_q1]

	subps	xmm0, xmm2

	movaps	xmm2, xmm0
	mulps	xmm0, xmm0

	paddd	xmm3, oword [_epi32_0x7f]

	mulps	xmm4, xmm0
	mulps	xmm6, xmm0
	addps	xmm4, xmm5
	addps	xmm6, xmm7

	mulps	xmm4, xmm0
	movaps	xmm5, oword [eax - 16]
	pslld	xmm3, 23
	addps	xmm4, oword [_ps_exp2_p2]

	mulps	xmm2, xmm4

	movaps	xmm0, oword [_ps_am_1]
	subps	xmm6, xmm2
	andps	xmm3, xmm5
	rcpps	xmm6, xmm6
	mulps	xmm2, xmm6
	addps	xmm2, xmm2
	addps	xmm0, xmm2

	mulps	xmm0, xmm3
    ret
    """
    
    avx_code = data + """

    #CODE
    global fast_pow_ps:
	vxorps	xmm5, xmm5, xmm5
	vcmpps xmm5, xmm5, xmm0, 1
	mov	eax , esp
	vmaxps	xmm0, xmm0, oword [ _ps_am_min_norm_pos]  ;// cut off denormalized stuff
	vmovaps	xmm7, oword [_ps_am_1]
	vmovaps	xmm3, xmm0
	and 	eax, 0xFFFFFFF0

	vandps	xmm0, xmm0, oword [_ps_am_inv_mant_mask]
	vorps	xmm0, xmm0, xmm7

	vmovaps	oword [eax - 16], xmm5

	vmovaps	xmm4, xmm0
	vsubps	xmm0, xmm0, xmm7
	vaddps	xmm4, xmm4, xmm7
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
	vmovaps	xmm5, oword [_ps_log2_c0]
	vaddps	xmm6, xmm6, xmm7
	vcvtdq2ps	xmm7, xmm3

	vmulps	xmm0, xmm0, xmm4
	vrcpps	xmm6, xmm6

	vmulps	xmm0, xmm0, xmm6
	vmovaps	xmm4, oword [_ps_exp2_hi]
	vmulps	xmm0, xmm0, xmm2
	vmovaps	xmm6, oword [_ps_exp2_lo]
	vmulps	xmm2, xmm2, xmm5
	vmulps	xmm0, xmm0, xmm5
	vaddps	xmm2, xmm2, xmm7
	vmovaps	xmm3, oword [_ps_am_0p5]
	vaddps	xmm0, xmm0, xmm2
	vxorps	xmm2, xmm2, xmm2

	vmulps	xmm0, xmm0, xmm1

	vminps	xmm0, xmm0, xmm4
	vmovaps	xmm4, oword [_ps_exp2_p0]
	vmaxps	xmm0, xmm0, xmm6
	vmovaps	xmm6, oword [_ps_exp2_q0]

	vaddps	xmm3, xmm3, xmm0

	vcmpps xmm2, xmm2, xmm3, 5
	vpand	xmm2, xmm2, oword [_epi32_1]

	vcvttps2dq	xmm3, xmm3

	vpsubd	xmm3, xmm3, xmm2
	vmovaps	xmm5, oword [_ps_exp2_p1]

	vcvtdq2ps	xmm2, xmm3
	vmovaps	xmm7, oword [_ps_exp2_q1]

	vsubps	xmm0, xmm0, xmm2

	vmovaps	xmm2, xmm0
	vmulps	xmm0, xmm0, xmm0

	vpaddd	xmm3, xmm3, oword [_epi32_0x7f]

	vmulps	xmm4, xmm4, xmm0
	vmulps	xmm6, xmm6, xmm0
	vaddps	xmm4, xmm4, xmm5
	vaddps	xmm6, xmm6, xmm7

	vmulps	xmm4, xmm4, xmm0
	vmovaps	xmm5, oword [eax - 16]
	vpslld	xmm3, xmm3, 23
	vaddps	xmm4, xmm4, oword [_ps_exp2_p2]

	vmulps	xmm2, xmm2, xmm4

	vmovaps	xmm0, oword [_ps_am_1]
	vsubps	xmm6, xmm6, xmm2
	vandps	xmm3, xmm3, xmm5
	vrcpps	xmm6, xmm6
	vmulps	xmm2, xmm2, xmm6
	vaddps	xmm2, xmm2, xmm2
	vaddps	xmm0, xmm0, xmm2

	vmulps	xmm0, xmm0, xmm3
    ret
    """

    asm = Tdasm()
    if util.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_pow_ps"  
    runtime.load(name, mc)

def atan_ss(runtime):
    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_m1[4] = -1.0, -1.0, -1.0, -1.0
    float _ps_atan_t0[4] = -0.091646118527, -0.091646118527, -0.091646118527, -0.091646118527
    float _ps_atan_s0[4] = 1.2797564625, 1.2797564625, 1.2797564625, 1.2797564625
    float _ps_atan_s1[4] = 2.1972168858, 2.1972168858, 2.1972168858, 2.1972168858
    float _ps_atan_t1[4] = -1.395694568, -1.395694568, -1.395694568, -1.395694568
    float _ps_atan_s2[4] = 6.8193064723, 6.8193064723, 6.8193064723 ,6.8193064723
    float _ps_atan_t2[4] = -94.3939261227, -94.3939261227, -94.3939261227, -94.3939261227
    float _ps_atan_s3[4] = 28.205206687, 28.205206687, 28.205206687, 28.205206687
    float _ps_atan_t3[4] = 12.888383034, 12.888383034, 12.888383034, 12.888383034
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679

    """
    asm_code = data + """

    #CODE
    global fast_atan_ss:
    movss	xmm1, dword [_ps_am_sign_mask]
	rcpss	xmm4, xmm0
	orps	xmm1, xmm0
	movss	xmm6, xmm4
	comiss	xmm1, dword [_ps_am_m1]
	movss	xmm3, dword [_ps_atan_t0]
	jnc		l_small  ; 'c' is 'lt' for comiss

    ;l_big:
	mulss	xmm6, xmm6

	movss	xmm5, dword [_ps_atan_s0]
	addss	xmm5, xmm6

	movss	xmm7, dword [_ps_atan_s1]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t1]
	addss	xmm7, xmm6
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_atan_s2]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t2]
	addss	xmm7, xmm6
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_atan_s3]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t3]
	addss	xmm7, xmm6
	movss	xmm2, dword [_ps_am_sign_mask]
	mulss	xmm4, xmm3
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_am_pi_o_2]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm4

	andps	xmm0, xmm2
	orps	xmm0, xmm7
	subss	xmm0, xmm5
	ret

    l_small:
	movaps	xmm2, xmm0
	mulss	xmm2, xmm2

	movss	xmm1, dword [_ps_atan_s0]
	addss	xmm1, xmm2

	movss	xmm7, dword [_ps_atan_s1]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t1]
	addss	xmm7, xmm2
	addss	xmm1, xmm7
			
	movss	xmm7, dword [_ps_atan_s2]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t2]
	addss	xmm7, xmm2
	addss	xmm1, xmm7

	movss	xmm7, dword [_ps_atan_s3]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t3]
	addss	xmm7, xmm2
	mulss	xmm0, xmm3
	addss	xmm1, xmm7

	rcpss	xmm1, xmm1
	mulss	xmm0, xmm1
    ret

    """
    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_atan_ss"  
    runtime.load(name, mc)

def atan_ps(runtime):
    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_am_m1[4] = -1.0, -1.0, -1.0, -1.0
    float _ps_atan_t0[4] = -0.091646118527, -0.091646118527, -0.091646118527, -0.091646118527
    float _ps_atan_s0[4] = 1.2797564625, 1.2797564625, 1.2797564625, 1.2797564625
    float _ps_atan_s1[4] = 2.1972168858, 2.1972168858, 2.1972168858, 2.1972168858
    float _ps_atan_t1[4] = -1.395694568, -1.395694568, -1.395694568, -1.395694568
    float _ps_atan_s2[4] = 6.8193064723, 6.8193064723, 6.8193064723 ,6.8193064723
    float _ps_atan_t2[4] = -94.3939261227, -94.3939261227, -94.3939261227, -94.3939261227
    float _ps_atan_s3[4] = 28.205206687, 28.205206687, 28.205206687, 28.205206687
    float _ps_atan_t3[4] = 12.888383034, 12.888383034, 12.888383034, 12.888383034
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679

    """
    asm_code = data + """

    #CODE
    global fast_atan_ps:
    movaps	xmm5, oword [_ps_am_1]
	movaps	xmm6, oword [_ps_am_m1]
	rcpps	xmm4, xmm0

	cmpps	xmm5, xmm0, 1
	cmpps	xmm6, xmm0, 6
	movaps	xmm1, oword [_ps_atan_s0]
	orps	xmm5, xmm6

	andps	xmm4, xmm5
	movaps	xmm2, oword [_ps_atan_t0]
	movaps	xmm7, xmm5
	andnps	xmm5, xmm0
	movaps	xmm3, oword [_ps_atan_s1]
	orps	xmm4, xmm5
	movaps	xmm0, xmm4

	movaps	xmm6, oword [_ps_atan_t1]
	mulps	xmm4, xmm4

	addps	xmm1, xmm4
	movaps	xmm5, oword [_ps_atan_s2]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm2
	movaps	xmm2, oword [_ps_atan_t2]
	addps	xmm3, xmm4
	addps	xmm1, xmm3

	movaps	xmm3, oword [_ps_atan_s3]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm6
	movaps	xmm6, oword [_ps_atan_t3]
	addps	xmm5, xmm4
	addps	xmm1, xmm5

	movaps	xmm5, oword [_ps_am_sign_mask]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm2
	addps	xmm3, xmm4
	movaps	xmm4, oword [_ps_am_pi_o_2]
	mulps	xmm6, xmm0
	addps	xmm1, xmm3

	andps	xmm0, xmm5
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm6

	orps	xmm0, xmm4
	subps	xmm0, xmm1

	andps	xmm0, xmm7
	andnps	xmm7, xmm1
	orps	xmm0, xmm7
	ret

    """

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_atan_ps"  
    runtime.load(name, mc)

def asin_ss(runtime):
    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_m1[4] = -1.0, -1.0, -1.0, -1.0
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_atan_t0[4] = -0.091646118527, -0.091646118527, -0.091646118527, -0.091646118527
    float _ps_atan_s0[4] = 1.2797564625, 1.2797564625, 1.2797564625, 1.2797564625
    float _ps_atan_s1[4] = 2.1972168858, 2.1972168858, 2.1972168858, 2.1972168858
    float _ps_atan_t1[4] = -1.395694568, -1.395694568, -1.395694568, -1.395694568
    float _ps_atan_s2[4] = 6.8193064723, 6.8193064723, 6.8193064723 ,6.8193064723
    float _ps_atan_t2[4] = -94.3939261227, -94.3939261227, -94.3939261227, -94.3939261227
    float _ps_atan_s3[4] = 28.205206687, 28.205206687, 28.205206687, 28.205206687
    float _ps_atan_t3[4] = 12.888383034, 12.888383034, 12.888383034, 12.888383034
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679

    """
    asm_code = data + """

    #CODE
    global fast_asin_ss:
    movss xmm1, dword [_ps_am_1]
    movss xmm2, xmm1
    addss xmm1, xmm0
    subss xmm2, xmm0
    mulss xmm1, xmm2
    rsqrtss xmm1, xmm1
    mulss xmm0, xmm1

    ;atan
    movss	xmm1, dword [_ps_am_sign_mask]
	rcpss	xmm4, xmm0
	orps	xmm1, xmm0
	movss	xmm6, xmm4
	comiss	xmm1, dword [_ps_am_m1]
	movss	xmm3, dword [_ps_atan_t0]
	jnc		l_small  ; 'c' is 'lt' for comiss

    ;l_big:
	mulss	xmm6, xmm6

	movss	xmm5, dword [_ps_atan_s0]
	addss	xmm5, xmm6

	movss	xmm7, dword [_ps_atan_s1]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t1]
	addss	xmm7, xmm6
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_atan_s2]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t2]
	addss	xmm7, xmm6
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_atan_s3]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t3]
	addss	xmm7, xmm6
	movss	xmm2, dword [_ps_am_sign_mask]
	mulss	xmm4, xmm3
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_am_pi_o_2]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm4

	andps	xmm0, xmm2
	orps	xmm0, xmm7
	subss	xmm0, xmm5
	ret

    l_small:
	movaps	xmm2, xmm0
	mulss	xmm2, xmm2

	movss	xmm1, dword [_ps_atan_s0]
	addss	xmm1, xmm2

	movss	xmm7, dword [_ps_atan_s1]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t1]
	addss	xmm7, xmm2
	addss	xmm1, xmm7
			
	movss	xmm7, dword [_ps_atan_s2]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t2]
	addss	xmm7, xmm2
	addss	xmm1, xmm7

	movss	xmm7, dword [_ps_atan_s3]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t3]
	addss	xmm7, xmm2
	mulss	xmm0, xmm3
	addss	xmm1, xmm7

	rcpss	xmm1, xmm1
	mulss	xmm0, xmm1
    ret

    """
    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_asin_ss"  
    runtime.load(name, mc)

def asin_ps(runtime):
    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_am_m1[4] = -1.0, -1.0, -1.0, -1.0
    float _ps_atan_t0[4] = -0.091646118527, -0.091646118527, -0.091646118527, -0.091646118527
    float _ps_atan_s0[4] = 1.2797564625, 1.2797564625, 1.2797564625, 1.2797564625
    float _ps_atan_s1[4] = 2.1972168858, 2.1972168858, 2.1972168858, 2.1972168858
    float _ps_atan_t1[4] = -1.395694568, -1.395694568, -1.395694568, -1.395694568
    float _ps_atan_s2[4] = 6.8193064723, 6.8193064723, 6.8193064723 ,6.8193064723
    float _ps_atan_t2[4] = -94.3939261227, -94.3939261227, -94.3939261227, -94.3939261227
    float _ps_atan_s3[4] = 28.205206687, 28.205206687, 28.205206687, 28.205206687
    float _ps_atan_t3[4] = 12.888383034, 12.888383034, 12.888383034, 12.888383034
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679

    """
    asm_code = data + """

    #CODE
    global fast_asin_ps:
    movaps xmm1, oword [_ps_am_1]
    movaps xmm2, xmm1
    addps xmm1, xmm0
    subps xmm2, xmm0
    mulps xmm1, xmm2
    rsqrtps xmm1, xmm1
    mulps xmm0, xmm1

    ;atan
    movaps	xmm5, oword [_ps_am_1]
	movaps	xmm6, oword [_ps_am_m1]
	rcpps	xmm4, xmm0

	cmpps	xmm5, xmm0, 1
	cmpps	xmm6, xmm0, 6
	movaps	xmm1, oword [_ps_atan_s0]
	orps	xmm5, xmm6

	andps	xmm4, xmm5
	movaps	xmm2, oword [_ps_atan_t0]
	movaps	xmm7, xmm5
	andnps	xmm5, xmm0
	movaps	xmm3, oword [_ps_atan_s1]
	orps	xmm4, xmm5
	movaps	xmm0, xmm4

	movaps	xmm6, oword [_ps_atan_t1]
	mulps	xmm4, xmm4

	addps	xmm1, xmm4
	movaps	xmm5, oword [_ps_atan_s2]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm2
	movaps	xmm2, oword [_ps_atan_t2]
	addps	xmm3, xmm4
	addps	xmm1, xmm3

	movaps	xmm3, oword [_ps_atan_s3]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm6
	movaps	xmm6, oword [_ps_atan_t3]
	addps	xmm5, xmm4
	addps	xmm1, xmm5

	movaps	xmm5, oword [_ps_am_sign_mask]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm2
	addps	xmm3, xmm4
	movaps	xmm4, oword [_ps_am_pi_o_2]
	mulps	xmm6, xmm0
	addps	xmm1, xmm3

	andps	xmm0, xmm5
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm6

	orps	xmm0, xmm4
	subps	xmm0, xmm1

	andps	xmm0, xmm7
	andnps	xmm7, xmm1
	orps	xmm0, xmm7
	ret

    """

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_sin_ps"  
    runtime.load(name, mc)

def acos_ss(runtime):
    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_m1[4] = -1.0, -1.0, -1.0, -1.0
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_atan_t0[4] = -0.091646118527, -0.091646118527, -0.091646118527, -0.091646118527
    float _ps_atan_s0[4] = 1.2797564625, 1.2797564625, 1.2797564625, 1.2797564625
    float _ps_atan_s1[4] = 2.1972168858, 2.1972168858, 2.1972168858, 2.1972168858
    float _ps_atan_t1[4] = -1.395694568, -1.395694568, -1.395694568, -1.395694568
    float _ps_atan_s2[4] = 6.8193064723, 6.8193064723, 6.8193064723 ,6.8193064723
    float _ps_atan_t2[4] = -94.3939261227, -94.3939261227, -94.3939261227, -94.3939261227
    float _ps_atan_s3[4] = 28.205206687, 28.205206687, 28.205206687, 28.205206687
    float _ps_atan_t3[4] = 12.888383034, 12.888383034, 12.888383034, 12.888383034
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679

    """
    asm_code = data + """

    #CODE
    global fast_acos_ss:
    movss xmm1, dword [_ps_am_1]
    movss xmm2, xmm1
    subss xmm1, xmm0
    addss xmm2, xmm0
    rcpss xmm1, xmm1
    mulss xmm2, xmm1
    rsqrtss xmm0, xmm2

    ;atan
    movss	xmm1, dword [_ps_am_sign_mask]
	rcpss	xmm4, xmm0
	orps	xmm1, xmm0
	movss	xmm6, xmm4
	comiss	xmm1, dword [_ps_am_m1]
	movss	xmm3, dword [_ps_atan_t0]
	jnc		l_small  ; 'c' is 'lt' for comiss

    ;l_big:
	mulss	xmm6, xmm6

	movss	xmm5, dword [_ps_atan_s0]
	addss	xmm5, xmm6

	movss	xmm7, dword [_ps_atan_s1]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t1]
	addss	xmm7, xmm6
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_atan_s2]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t2]
	addss	xmm7, xmm6
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_atan_s3]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm3
	movss	xmm3, dword [_ps_atan_t3]
	addss	xmm7, xmm6
	movss	xmm2, dword [_ps_am_sign_mask]
	mulss	xmm4, xmm3
	addss	xmm5, xmm7

	movss	xmm7, dword [_ps_am_pi_o_2]
	rcpss	xmm5, xmm5
	mulss	xmm5, xmm4

	andps	xmm0, xmm2
	orps	xmm0, xmm7
	subss	xmm0, xmm5
	ret

    l_small:
	movaps	xmm2, xmm0
	mulss	xmm2, xmm2

	movss	xmm1, dword [_ps_atan_s0]
	addss	xmm1, xmm2

	movss	xmm7, dword [_ps_atan_s1]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t1]
	addss	xmm7, xmm2
	addss	xmm1, xmm7
			
	movss	xmm7, dword [_ps_atan_s2]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t2]
	addss	xmm7, xmm2
	addss	xmm1, xmm7

	movss	xmm7, dword [_ps_atan_s3]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm3
	movss	xmm3, dword [_ps_atan_t3]
	addss	xmm7, xmm2
	mulss	xmm0, xmm3
	addss	xmm1, xmm7

	rcpss	xmm1, xmm1
	mulss	xmm0, xmm1

    addss xmm0, xmm0 ;this line is not part of atan 
    ret

    """
    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_acos_ss"  
    runtime.load(name, mc)

def acos_ps(runtime):
    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_am_m1[4] = -1.0, -1.0, -1.0, -1.0
    float _ps_atan_t0[4] = -0.091646118527, -0.091646118527, -0.091646118527, -0.091646118527
    float _ps_atan_s0[4] = 1.2797564625, 1.2797564625, 1.2797564625, 1.2797564625
    float _ps_atan_s1[4] = 2.1972168858, 2.1972168858, 2.1972168858, 2.1972168858
    float _ps_atan_t1[4] = -1.395694568, -1.395694568, -1.395694568, -1.395694568
    float _ps_atan_s2[4] = 6.8193064723, 6.8193064723, 6.8193064723 ,6.8193064723
    float _ps_atan_t2[4] = -94.3939261227, -94.3939261227, -94.3939261227, -94.3939261227
    float _ps_atan_s3[4] = 28.205206687, 28.205206687, 28.205206687, 28.205206687
    float _ps_atan_t3[4] = 12.888383034, 12.888383034, 12.888383034, 12.888383034
    float _ps_am_pi_o_2[4] = 1.57079632679, 1.57079632679, 1.57079632679, 1.57079632679

    """
    asm_code = data + """

    #CODE
    global fast_acos_ps:
    movaps xmm1, oword [_ps_am_1]
    movaps xmm2, xmm1
    subps xmm1, xmm0
    addps xmm2, xmm0
    rcpps xmm1, xmm1
    mulps xmm2, xmm1
    rsqrtps xmm0, xmm2

    ;atan
    movaps	xmm5, oword [_ps_am_1]
	movaps	xmm6, oword [_ps_am_m1]
	rcpps	xmm4, xmm0

	cmpps	xmm5, xmm0, 1
	cmpps	xmm6, xmm0, 6
	movaps	xmm1, oword [_ps_atan_s0]
	orps	xmm5, xmm6

	andps	xmm4, xmm5
	movaps	xmm2, oword [_ps_atan_t0]
	movaps	xmm7, xmm5
	andnps	xmm5, xmm0
	movaps	xmm3, oword [_ps_atan_s1]
	orps	xmm4, xmm5
	movaps	xmm0, xmm4

	movaps	xmm6, oword [_ps_atan_t1]
	mulps	xmm4, xmm4

	addps	xmm1, xmm4
	movaps	xmm5, oword [_ps_atan_s2]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm2
	movaps	xmm2, oword [_ps_atan_t2]
	addps	xmm3, xmm4
	addps	xmm1, xmm3

	movaps	xmm3, oword [_ps_atan_s3]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm6
	movaps	xmm6, oword [_ps_atan_t3]
	addps	xmm5, xmm4
	addps	xmm1, xmm5

	movaps	xmm5, oword [_ps_am_sign_mask]
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm2
	addps	xmm3, xmm4
	movaps	xmm4, oword [_ps_am_pi_o_2]
	mulps	xmm6, xmm0
	addps	xmm1, xmm3

	andps	xmm0, xmm5
	rcpps	xmm1, xmm1
	mulps	xmm1, xmm6

	orps	xmm0, xmm4
	subps	xmm0, xmm1

	andps	xmm0, xmm7
	andnps	xmm7, xmm1
	orps	xmm0, xmm7

    addps xmm0, xmm0 ;this line is not part of atan 
	ret

    """

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_acos_ps"  
    runtime.load(name, mc)

def tan_ss(runtime):
    data = """
    #DATA
    uint32 _ps_am_inv_sign_mask[4] = 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF, 0x7FFFFFFF
    float _ps_am_4_o_pi[4] = 1.273239544735, 1.273239544735, 1.273239544735, 1.273239544735
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_am_pi_o_4[4] = 0.78539816339, 0.78539816339, 0.78539816339, 0.78539816339
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
    global fast_tan_ss:
    movss	xmm1, dword [_ps_am_inv_sign_mask]
    movd	eax, xmm0
    andps	xmm0, xmm1
    movaps	xmm1, xmm0
    mulss	xmm0, dword [_ps_am_4_o_pi]

    cvttss2si	edx, xmm0
    and		eax, 0x80000000

    mov		ecx, 0x1
    movd	xmm7, eax
    mov		eax, 0x7

    movss	xmm5, dword [_ps_am_1]

    and		ecx, edx
    and		eax, edx
    add		edx, ecx
    add		eax, ecx

    cvtsi2ss	xmm0, edx
    xorps	xmm6, xmm6

    mulss	xmm0, dword [_ps_am_pi_o_4]
    subss	xmm1, xmm0
    movss	xmm2, dword [_ps_tan_p2]
    minss	xmm1, xmm5
    movss	xmm3, dword [_ps_tan_q3]
    movaps	xmm0, xmm1
    mulss	xmm1, xmm1

    mulss	xmm2, xmm1
    addss	xmm3, xmm1
    addss	xmm2, dword [_ps_tan_p1]
    mulss	xmm3, xmm1
    mulss	xmm2, xmm1
    addss	xmm3, dword [_ps_tan_q2]
    addss	xmm2, dword [_ps_tan_p0]
    mulss	xmm3, xmm1
    mulss	xmm2, xmm1
    addss	xmm3, dword [_ps_tan_q1]
    xorps	xmm0, xmm7
    mulss	xmm3, xmm1
    mulss	xmm2, xmm0
    addss	xmm3, dword [_ps_tan_q0]

    rcpss	xmm4, xmm3
    mulss	xmm3, xmm4
    mulss	xmm3, xmm4
    addss	xmm4, xmm4
    test	eax, 0x2
    subss	xmm4, xmm3

    mulss	xmm2, xmm4
    jz		l_cont
    addss	xmm2, xmm0
    comiss	xmm6, xmm1

    rcpss	xmm4, xmm2
    movss	xmm0, dword [_ps_am_sign_mask]
    jz		l_pole
    mulss	xmm2, xmm4
    mulss	xmm2, xmm4
    addss	xmm4, xmm4
    subss	xmm4, xmm2
    xorps	xmm0, xmm4

    ret		

    l_pole:
    movss	xmm1, dword [_ps_tan_poleval]
    movaps	xmm3, xmm0
    andps	xmm0, xmm2
    orps	xmm0, xmm1

    xorps	xmm0, xmm3

    ret		

    l_cont:
    addss	xmm0, xmm2
    ret		


    """

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_tan_ss"  
    runtime.load(name, mc)

def tan_ps(runtime):
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

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_tan_ps"  
    runtime.load(name, mc)

def log_ss(runtime):
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
    global fast_log_ss:
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

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_log_ss"  
    runtime.load(name, mc)

def log_ps(runtime):
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
    global fast_log_ps:
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

    asm = Tdasm()
    if util.AVX:
        raise ValueError("AVX is not yet implemented")
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    name = "fast_log_ps"  
    runtime.load(name, mc)

## Function that is used to load transcendental function in runtime(memory). Thease functions destroys registers
# xmm0 - xmm7 and only fast_pow_ps also destroy register eax.
# @param name Name of function to load in runtime(memory). 
# Currntly supported functions. \n
# fast_sin_ss - Input xmm0[0:32]    Output xmm0[0:32] = sinus(xmm0[0:32])\n
# fast_sin_ps = Input xmm0,         Output xmm0 = sinus(xmm0) \n
# fast_cos_ss - Input xmm0[0:32],   Output xmm0 = cosinus(xmm[0:32]) \n
# fast_cos_ps - Input xmm0, Output xmm0 \n
# fast_sincos_ss - Input xmm0[0:32] , Output sinus = xmm0[0:32], cosinus = xmm6[0:32] \n
# fast_sincos_ps - Input xmm0, Output sinus = xmm0, cosinus = xmm6 \n
# fast_exp_ss - Input xmm0[0:32], Output - xmm0[0:32] \n
# fast_exp_ps - Input xmm0, Output - xmm0 \n
# fast_pow_ss - Input xmm0[0:32], xmm1[0:32], Output - xmm[0:32] = xmm0[0:32] ^ xmm1[0:32] \n
# fast_pow_ps - Input xmm0, xmm1  - Output - xmm0 = xmm0 ^ xmm1 \n
# @param runtime Runtime object that will hold machine code of function
# @return True if function is loaded in memory 
def load_math_func(name, runtime):

    funcs = { "fast_sin_ss": sin_ss,
            "fast_sin_ps": sin_ps,
            "fast_pow_ss": pow_ss,
            "fast_pow_ps": pow_ps,
            "fast_cos_ss": cos_ss,
            "fast_cos_ps": cos_ps,
            "fast_sincos_ss": sincos_ss,
            "fast_sincos_ps": sincos_ps,
            "fast_exp_ss": exp_ss,
            "fast_exp_ps": exp_ps,
            "fast_atan_ss": atan_ss,
            "fast_atan_ps": atan_ps,
            "fast_asin_ss": asin_ss,
            "fast_asin_ps": asin_ps,
            "fast_acos_ss": acos_ss,
            "fast_acos_ps": acos_ps,
            "fast_tan_ss": tan_ss,
            "fast_tan_ps": tan_ps,
            "fast_log_ss": log_ss,
            "fast_log_ps": log_ps
            }

    if name in funcs:
        if not runtime.global_exists(name):
            funcs[name](runtime)
            return True
        return True

    #FIXME trhow exception
    return False


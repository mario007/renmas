
import renmas3.switch as proc
from tdasm import Tdasm

def tan_ss():
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

    avx_code = data + """

    #CODE
    global fast_tan_ss:
    vmovss	xmm1, dword [_ps_am_inv_sign_mask]
    vmovd	eax, xmm0
    vandps	xmm0, xmm0, xmm1
    vmovaps	xmm1, xmm0
    vmulss	xmm0, xmm0, dword [_ps_am_4_o_pi]

    vcvttss2si	edx, xmm0
    and		eax, 0x80000000

    mov		ecx, 0x1
    vmovd	xmm7, eax
    mov		eax, 0x7

    vmovss	xmm5, dword [_ps_am_1]

    and		ecx, edx
    and		eax, edx
    add		edx, ecx
    add		eax, ecx

    vcvtsi2ss	xmm0, xmm0, edx
    vxorps	xmm6, xmm6, xmm6

    vmulss	xmm0, xmm0, dword [_ps_am_pi_o_4]
    vsubss	xmm1, xmm1, xmm0
    vmovss	xmm2, dword [_ps_tan_p2]
    vminss	xmm1, xmm1, xmm5
    vmovss	xmm3, dword [_ps_tan_q3]
    vmovaps	xmm0, xmm1
    vmulss	xmm1, xmm1, xmm1

    vmulss	xmm2, xmm2, xmm1
    vaddss	xmm3, xmm3, xmm1
    vaddss	xmm2, xmm2, dword [_ps_tan_p1]
    vmulss	xmm3, xmm3, xmm1
    vmulss	xmm2, xmm2, xmm1
    vaddss	xmm3, xmm3, dword [_ps_tan_q2]
    vaddss	xmm2, xmm2, dword [_ps_tan_p0]
    vmulss	xmm3, xmm3, xmm1
    vmulss	xmm2, xmm2, xmm1
    vaddss	xmm3, xmm3, dword [_ps_tan_q1]
    vxorps	xmm0, xmm0, xmm7
    vmulss	xmm3, xmm3, xmm1
    vmulss	xmm2, xmm2, xmm0
    vaddss	xmm3, xmm3, dword [_ps_tan_q0]

    vrcpss	xmm4, xmm4, xmm3
    vmulss	xmm3, xmm3, xmm4
    vmulss	xmm3, xmm3, xmm4
    vaddss	xmm4, xmm4, xmm4
    test	eax, 0x2
    vsubss	xmm4, xmm4, xmm3

    vmulss	xmm2, xmm2, xmm4
    jz		l_cont
    vaddss	xmm2, xmm2, xmm0
    vcomiss	xmm6, xmm1

    vrcpss	xmm4, xmm4, xmm2
    vmovss	xmm0, dword [_ps_am_sign_mask]
    jz		l_pole
    vmulss	xmm2, xmm2, xmm4
    vmulss	xmm2, xmm2, xmm4
    vaddss	xmm4, xmm4, xmm4
    vsubss	xmm4, xmm4, xmm2
    vxorps	xmm0, xmm0, xmm4

    ret		

    l_pole:
    vmovss	xmm1, dword [_ps_tan_poleval]
    vmovaps	xmm3, xmm0
    vandps	xmm0, xmm0, xmm2
    vorps	xmm0, xmm0, xmm1

    vxorps	xmm0, xmm0, xmm3

    ret		

    l_cont:
    vaddss	xmm0, xmm0, xmm2
    ret		


    """

    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    return mc


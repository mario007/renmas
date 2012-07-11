import platform

import renmas3.switch as proc
from tdasm import Tdasm

def atanr2_ss():

    bits = platform.architecture()[0]

    data = """
    #DATA
    uint32 _ps_am_sign_mask[4] = 0x80000000, 0x80000000, 0x80000000, 0x80000000
    float _ps_am_1[4] = 1.0, 1.0, 1.0, 1.0
    float _ps_am_pi[4] = 3.141592653589, 3.141592653589, 3.141592653589, 3.141592653589
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
    global fast_atanr2_ss:
    movss	xmm2, dword [_ps_am_sign_mask]
	xorps	xmm3, xmm3
	movss	xmm5, dword [_ps_am_1]
	andps	xmm2, xmm0
	mulss	xmm0, xmm1
	orps	xmm2, oword [_ps_am_pi]
	cmpss	xmm3, xmm1, 2

	movss	xmm6, dword [_ps_am_m1]
	rcpss	xmm4, xmm0

	cmpss	xmm5, xmm0, 1
	cmpss	xmm6, xmm0, 6
	movss	xmm1, dword [_ps_atan_s0]
	orps	xmm5, xmm6
    """
    if bits == '64bit':
        asm_code += "movss	dword [rsp - 4], xmm2\n"
        asm_code += "movss	dword [rsp - 8], xmm3\n"
    else:
        asm_code += "movss	dword [esp - 4], xmm2\n"
        asm_code += "movss	dword [esp - 8], xmm3\n"

    asm_code += """
	andps	xmm4, xmm5
	movss	xmm2, dword [_ps_atan_t0]
	movaps	xmm7, xmm5
	andnps	xmm5, xmm0
	movss	xmm3, dword [_ps_atan_s1]
	orps	xmm4, xmm5
	movaps	xmm0, xmm4

	movss	xmm6, dword [_ps_atan_t1]
	mulss	xmm4, xmm4

	addss	xmm1, xmm4
	movss	xmm5, dword [_ps_atan_s2]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm2
	movss	xmm2, dword [_ps_atan_t2]
	addss	xmm3, xmm4
	addss	xmm1, xmm3

	movss	xmm3, dword [_ps_atan_s3]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm6
	movss	xmm6, dword [_ps_atan_t3]
	addss	xmm5, xmm4
	addss	xmm1, xmm5

	movss	xmm5, dword [_ps_am_sign_mask]
	rcpss	xmm1, xmm1
	mulss	xmm1, xmm2
	addss	xmm3, xmm4
	movss	xmm4, dword [_ps_am_pi_o_2]
	mulss	xmm6, xmm0
	addss	xmm1, xmm3

	andps	xmm0, xmm5
	rcpss	xmm1, xmm1
    """
    if bits == '64bit':
        asm_code += "movss	xmm3, dword [rsp - 8]\n"
    else:
        asm_code += "movss	xmm3, dword [esp - 8]\n"

    asm_code += """
	mulss	xmm1, xmm6

	orps	xmm0, xmm4
	subss	xmm0, xmm1
    """
    if bits == '64bit':
        asm_code += "movss	xmm2, dword [rsp - 4]\n"
    else:
        asm_code += "movss	xmm2, dword [esp - 4]\n"

    asm_code += """
	andps	xmm0, xmm7
	andnps	xmm7, xmm1
	orps	xmm0, xmm7

	movaps	xmm1, xmm0
	andps	xmm0, xmm3
	addss	xmm1, xmm2
	andnps	xmm3, xmm1
	orps	xmm0, xmm3

	ret
    """
    
    avx_code = data + """
    #CODE
    global fast_atanr2_ss:
    vmovss	xmm2, dword [_ps_am_sign_mask]
	vxorps	xmm3, xmm3, xmm3
	vmovss	xmm5, dword [_ps_am_1]
	vandps	xmm2, xmm2, xmm0
	vmulss	xmm0, xmm0, xmm1
	vorps	xmm2, xmm2, oword [_ps_am_pi]
	vcmpss	xmm3, xmm3, xmm1, 2

	vmovss	xmm6, dword [_ps_am_m1]
	vrcpss	xmm4, xmm4, xmm0

	vcmpss	xmm5, xmm5, xmm0, 1
	vcmpss	xmm6, xmm6, xmm0, 6
	vmovss	xmm1, dword [_ps_atan_s0]
	vorps	xmm5, xmm5, xmm6
    """
    if bits == '64bit':
        avx_code += "vmovss	dword [rsp - 4], xmm2\n"
        avx_code += "vmovss	dword [rsp - 8], xmm3\n"
    else:
        avx_code += "vmovss	dword [esp - 4], xmm2\n"
        avx_code += "vmovss	dword [esp - 8], xmm3\n"

    avx_code += """
	vandps	xmm4, xmm4, xmm5
	vmovss	xmm2, dword [_ps_atan_t0]
	vmovaps	xmm7, xmm5
	vandnps	xmm5, xmm5, xmm0
	vmovss	xmm3, dword [_ps_atan_s1]
	vorps	xmm4, xmm4, xmm5
	vmovaps	xmm0, xmm4

	vmovss	xmm6, dword [_ps_atan_t1]
	vmulss	xmm4, xmm4, xmm4

	vaddss	xmm1, xmm1, xmm4
	vmovss	xmm5, dword [_ps_atan_s2]
	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm1, xmm1, xmm2
	vmovss	xmm2, dword [_ps_atan_t2]
	vaddss	xmm3, xmm3, xmm4
	vaddss	xmm1, xmm1, xmm3

	vmovss	xmm3, dword [_ps_atan_s3]
	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm1, xmm1, xmm6
	vmovss	xmm6, dword [_ps_atan_t3]
	vaddss	xmm5, xmm5, xmm4
	vaddss	xmm1, xmm1, xmm5

	vmovss	xmm5, dword [_ps_am_sign_mask]
	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm1, xmm1, xmm2
	vaddss	xmm3, xmm3, xmm4
	vmovss	xmm4, dword [_ps_am_pi_o_2]
	vmulss	xmm6, xmm6, xmm0
	vaddss	xmm1, xmm1, xmm3

	vandps	xmm0, xmm0, xmm5
	vrcpss	xmm1, xmm1, xmm1
    """
    if bits == '64bit':
        avx_code += "vmovss	xmm3, dword [rsp - 8]\n"
    else:
        avx_code += "vmovss	xmm3, dword [esp - 8]\n"

    avx_code += """
	vmulss	xmm1, xmm1, xmm6

	vorps	xmm0, xmm0, xmm4
	vsubss	xmm0, xmm0, xmm1
    """
    if bits == '64bit':
        avx_code += "vmovss	xmm2, dword [rsp - 4]\n"
    else:
        avx_code += "vmovss	xmm2, dword [esp - 4]\n"

    avx_code += """
	vandps	xmm0, xmm0, xmm7
	vandnps	xmm7, xmm7, xmm1
	vorps	xmm0, xmm0, xmm7

	vmovaps	xmm1, xmm0
	vandps	xmm0, xmm0, xmm3
	vaddss	xmm1, xmm1, xmm2
	vandnps	xmm3, xmm3, xmm1
	vorps	xmm0, xmm0, xmm3

	ret
    """

    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    return mc



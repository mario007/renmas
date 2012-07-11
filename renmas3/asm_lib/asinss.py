
import renmas3.switch as proc
from tdasm import Tdasm

def asin_ss():
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

    avx_code = data + """

    #CODE
    global fast_asin_ss:
    vmovss xmm1, dword [_ps_am_1]
    vmovss xmm2, xmm2, xmm1
    vaddss xmm1, xmm1, xmm0
    vsubss xmm2, xmm2, xmm0
    vmulss xmm1, xmm1, xmm2
    vrsqrtss xmm1, xmm1, xmm1
    vmulss xmm0, xmm0, xmm1

    ;atan
    vmovss	xmm1, dword [_ps_am_sign_mask]
	vrcpss	xmm4, xmm4, xmm0
	vorps	xmm1, xmm1, xmm0
	vmovss	xmm6, xmm6, xmm4
	vcomiss	xmm1, dword [_ps_am_m1]
	vmovss	xmm3, dword [_ps_atan_t0]
	jnc		l_small  ; 'c' is 'lt' for comiss

    ;l_big:
	vmulss	xmm6, xmm6, xmm6

	vmovss	xmm5, dword [_ps_atan_s0]
	vaddss	xmm5, xmm5, xmm6

	vmovss	xmm7, dword [_ps_atan_s1]
	vrcpss	xmm5, xmm5, xmm5
	vmulss	xmm5, xmm5, xmm3
	vmovss	xmm3, dword [_ps_atan_t1]
	vaddss	xmm7, xmm7, xmm6
	vaddss	xmm5, xmm5, xmm7

	vmovss	xmm7, dword [_ps_atan_s2]
	vrcpss	xmm5, xmm5, xmm5
	vmulss	xmm5, xmm5, xmm3
	vmovss	xmm3, dword [_ps_atan_t2]
	vaddss	xmm7, xmm7, xmm6
	vaddss	xmm5, xmm5, xmm7

	vmovss	xmm7, dword [_ps_atan_s3]
	vrcpss	xmm5, xmm5, xmm5
	vmulss	xmm5, xmm5, xmm3
	vmovss	xmm3, dword [_ps_atan_t3]
	vaddss	xmm7, xmm7, xmm6
	vmovss	xmm2, dword [_ps_am_sign_mask]
	vmulss	xmm4, xmm4, xmm3
	vaddss	xmm5, xmm5, xmm7

	vmovss	xmm7, dword [_ps_am_pi_o_2]
	vrcpss	xmm5, xmm5, xmm5
	vmulss	xmm5, xmm5, xmm4

	vandps	xmm0, xmm0, xmm2
	vorps	xmm0, xmm0, xmm7
	vsubss	xmm0, xmm0, xmm5
	ret

    l_small:
	vmovaps	xmm2, xmm0
	vmulss	xmm2, xmm2, xmm2

	vmovss	xmm1, dword [_ps_atan_s0]
	vaddss	xmm1, xmm1, xmm2

	vmovss	xmm7, dword [_ps_atan_s1]
	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm1, xmm1, xmm3
	vmovss	xmm3, dword [_ps_atan_t1]
	vaddss	xmm7, xmm7, xmm2
	vaddss	xmm1, xmm1, xmm7
			
	vmovss	xmm7, dword [_ps_atan_s2]
	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm1, xmm1, xmm3
	vmovss	xmm3, dword [_ps_atan_t2]
	vaddss	xmm7, xmm7, xmm2
	vaddss	xmm1, xmm1, xmm7

	vmovss	xmm7, dword [_ps_atan_s3]
	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm1, xmm1, xmm3
	vmovss	xmm3, dword [_ps_atan_t3]
	vaddss	xmm7, xmm7, xmm2
	vmulss	xmm0, xmm0, xmm3
	vaddss	xmm1, xmm1, xmm7

	vrcpss	xmm1, xmm1, xmm1
	vmulss	xmm0, xmm0, xmm1
    ret

    """
    asm = Tdasm()
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    return mc



import renmas2.switch as proc
from tdasm import Tdasm

def atanr2_ps():
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
    global fast_atanr2_ps:
    movaps	xmm2, oword [_ps_am_sign_mask]
	xorps	xmm3, xmm3
	mov		ecx, esp
	movaps	xmm5, oword [_ps_am_1]
	andps	xmm2, xmm0
	mulps	xmm0, xmm1
	and 	ecx, 0xFFFFFFF0
	orps	xmm2, oword [_ps_am_pi]
	cmpps	xmm3, xmm1, 2 
	movaps	xmm6, oword [_ps_am_m1]
	rcpps	xmm4, xmm0

	cmpps	xmm5, xmm0, 1
	cmpps	xmm6, xmm0, 6
	movaps	xmm1, oword [_ps_atan_s0]
	orps	xmm5, xmm6

	movaps	oword [ecx - 16], xmm2
	movaps	oword [ecx - 32], xmm3

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
	movaps	xmm3, oword [ecx - 32]
	mulps	xmm1, xmm6

	orps	xmm0, xmm4
	subps	xmm0, xmm1
	movaps	xmm2, oword [ecx - 16]

	andps	xmm0, xmm7
	andnps	xmm7, xmm1
	orps	xmm0, xmm7

	movaps	xmm1, xmm0
	andps	xmm0, xmm3
	addps	xmm1, xmm2
	andnps	xmm3, xmm1
	orps	xmm0, xmm3

	ret
    """

    avx_code = data + """
    #CODE
    global fast_atanr2_ps:
    vmovaps	xmm2, oword [_ps_am_sign_mask]
	vxorps	xmm3, xmm3, xmm3
	mov		ecx, esp
	vmovaps	xmm5, oword [_ps_am_1]
	vandps	xmm2, xmm2, xmm0
	vmulps	xmm0, xmm0, xmm1
	and 	ecx, 0xFFFFFFF0
	vorps	xmm2, xmm2, oword [_ps_am_pi]
	vcmpps	xmm3, xmm3, xmm1, 2 
	vmovaps	xmm6, oword [_ps_am_m1]
	vrcpps	xmm4, xmm0

	vcmpps	xmm5, xmm5, xmm0, 1
	vcmpps	xmm6, xmm6, xmm0, 6
	vmovaps	xmm1, oword [_ps_atan_s0]
	vorps	xmm5, xmm5, xmm6

	vmovaps	oword [ecx - 16], xmm2
	vmovaps	oword [ecx - 32], xmm3

	vandps	xmm4, xmm4, xmm5
	vmovaps	xmm2, oword [_ps_atan_t0]
	vmovaps	xmm7, xmm5
	vandnps	xmm5, xmm5, xmm0
	vmovaps	xmm3, oword [_ps_atan_s1]
	vorps	xmm4, xmm4, xmm5
	vmovaps	xmm0, xmm4

	vmovaps	xmm6, oword [_ps_atan_t1]
	vmulps	xmm4, xmm4, xmm4

	vaddps	xmm1, xmm1, xmm4
	vmovaps	xmm5, oword [_ps_atan_s2]
	vrcpps	xmm1, xmm1
	vmulps	xmm1, xmm1, xmm2
	vmovaps	xmm2, oword [_ps_atan_t2]
	vaddps	xmm3, xmm3, xmm4
	vaddps	xmm1, xmm1, xmm3

	vmovaps	xmm3, oword [_ps_atan_s3]
	vrcpps	xmm1, xmm1
	vmulps	xmm1, xmm1, xmm6
	vmovaps	xmm6, oword [_ps_atan_t3]
	vaddps	xmm5, xmm5, xmm4
	vaddps	xmm1, xmm1, xmm5

	vmovaps	xmm5, oword [_ps_am_sign_mask]
	vrcpps	xmm1, xmm1
	vmulps	xmm1, xmm1, xmm2
	vaddps	xmm3, xmm3, xmm4
	vmovaps	xmm4, oword [_ps_am_pi_o_2]
	vmulps	xmm6, xmm6, xmm0
	vaddps	xmm1, xmm1, xmm3

	vandps	xmm0, xmm0, xmm5
	vrcpps	xmm1, xmm1
	vmovaps	xmm3, oword [ecx - 32]
	vmulps	xmm1, xmm1, xmm6

	vorps	xmm0, xmm0, xmm4
	vsubps	xmm0, xmm0, xmm1
	vmovaps	xmm2, oword [ecx - 16]

	vandps	xmm0, xmm0, xmm7
	vandnps	xmm7, xmm7, xmm1
	vorps	xmm0, xmm0, xmm7

	vmovaps	xmm1, xmm0
	vandps	xmm0, xmm0, xmm3
	vaddps	xmm1, xmm1, xmm2
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


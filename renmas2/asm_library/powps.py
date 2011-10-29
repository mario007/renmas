
import renmas2.switch as proc
from tdasm import Tdasm

def pow_ps():
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
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)

    return mc

    #name = "fast_pow_ps"  
    #runtime.load(name, mc)


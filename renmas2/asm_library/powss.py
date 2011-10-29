
import renmas2.switch as proc
from tdasm import Tdasm

def pow_ss():
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
    if proc.AVX:
        mc = asm.assemble(avx_code, True)
    else:
        mc = asm.assemble(asm_code, True)
    
    return mc

    #name = "fast_pow_ss"  
    #runtime.load(name, mc)


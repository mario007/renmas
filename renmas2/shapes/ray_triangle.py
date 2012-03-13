
import renmas2.switch as proc

# eax = pointer to ray structure
# ecx = pointer to minimum distance
# esi = pointer to p0
# edi = pointer to p1
# ebp = pointer to p2

def ray_triangle_intersection():
    #eax - ray, ebx - flat mesh, ecx - distance, esi - p0, edi - p1, ebp - p2

    if proc.AVX:
        code = """
        vmovaps xmm0, oword [esi]
        vsubps xmm1, xmm0, oword [ebp]
        vsubps xmm3, xmm0, oword [eax + ray.origin]
        vmovaps xmm2, oword [eax + ray.dir]
        vsubps xmm0, xmm0, oword [edi]

        ; f f h f
        vmovlhps xmm4, xmm1, xmm3
        vpermilps xmm4, xmm4, 01110101B 

        ; k k k l
        vmovhlps xmm5, xmm2, xmm3
        vpermilps xmm5, xmm5, 00101010B 

        ; f f h f * k k k l
        vmulps xmm7, xmm4, xmm5

        ; g g g h
        vmovlhps xmm6, xmm2, xmm3
        vpermilps xmm6, xmm6, 11010101B 

        ; j j l j
        vmovhlps xmm4, xmm1, xmm3
        vpermilps xmm4, xmm4, 10001010B 

        ; g g g h * j j l j
        vmulps xmm4, xmm4, xmm6

        ; f f h f * k k k l - g g g h * j j l j
        vsubps xmm7, xmm7, xmm4

        ; a d a a
        vmovlhps xmm5, xmm0, xmm3
        vpermilps xmm5, xmm5, 00001000B 

        ; a d a a * (f f h f * k k k l - g g g h * j j l j)
        vmulps xmm7, xmm7, xmm5

        ; i l i i
        vmovhlps xmm5, xmm0, xmm3
        vpermilps xmm5, xmm5, 10100010B 

        ; g g g h * i l i i
        vmulps xmm6, xmm6, xmm5

        ; e h e e
        vmovlhps xmm4, xmm0, xmm3
        vpermilps xmm4, xmm4, 01011101B 

        ; k k k l
        vmovhlps xmm5, xmm2, xmm3
        vpermilps xmm5, xmm5, 00101010B 

        ; e h e e * k k k l
        vmulps xmm5, xmm5, xmm4

        ; g g g h * i l i i - e h e e * k k k l
        vsubps xmm6, xmm6, xmm5

        ; b b d b
        vmovlhps xmm5, xmm1, xmm3
        vpermilps xmm5, xmm5, 00100000B 

        ; b b d b * (g g g h * i l i i - e h e e * k k k l)
        vmulps xmm6, xmm6, xmm5

        vaddps xmm7, xmm7, xmm6

        ; j j l j
        vmovhlps xmm5, xmm1, xmm3
        vpermilps xmm5, xmm5, 10001010B 

        ; e e h e * j j l j 
        vmulps xmm4, xmm4, xmm5

        ; f f h f
        vmovlhps xmm6, xmm1, xmm3
        vpermilps xmm6, xmm6, 01110101B 

        ; i l i i
        vmovhlps xmm5, xmm0, xmm3
        vpermilps xmm5, xmm5, 10100010B 

        ; f f h f * i l i i
        vmulps xmm6, xmm6, xmm5

        ; e h e e * j j l j - f f h f * i l i i
        vsubps xmm4, xmm4, xmm6

        ; c c c d
        vmovlhps xmm5, xmm2, xmm3
        vpermilps xmm5, xmm5, 10000000B 

        ; c c c d * (e h e e * j j l j - f f h f * i l i i)
        vmulps xmm4, xmm4, xmm5

        vaddps xmm7, xmm7, xmm4

        vpermilps xmm3, xmm7, 00000000B 
        vdivps xmm7, xmm7, xmm3

        vpermilps xmm5, xmm7, 10101010B 
        vpermilps xmm4, xmm7, 01010101B 
        vpermilps xmm6, xmm7, 11111111B 

        ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta

        vpxor xmm3, xmm3, xmm3
        macro eq128 xmm2 = xmm4
        macro if xmm4 < xmm3 goto _reject_092
        macro if xmm5 < xmm3 goto _reject_092
        vaddss xmm4, xmm4, xmm5
        macro if xmm4 > one goto _reject_092

        vcomiss xmm6, dword [epsilon]
        jc _reject_092
        vcomiss xmm6, dword [ecx] ;minimum distance
        jnc _reject_092

        ;populate hitpoint structure
        ; t is in xmm6
        
        mov eax, 1
        jmp _accept_092

        _reject_092:
        xor eax, eax
        _accept_092:

        """
        
    else:
    #eax - ray, ebx - flat mesh, ecx - distance, esi - p0, edi - p1, ebp - p2
        code = """
        movaps xmm0, oword [esi]
        movaps xmm1, xmm0 
        movaps xmm3, xmm0
        subps xmm0, oword [edi]
        movaps xmm2, oword [eax + ray.dir]
        subps xmm1, oword [ebp]
        subps xmm3, oword [eax + ray.origin]

        ; f f h f
        movaps xmm4, xmm1
        movlhps xmm4, xmm3
        shufps xmm4, xmm4, 01110101B

        ; k k k l
        movaps xmm5, xmm2
        movhlps xmm5, xmm3
        shufps xmm5, xmm5, 00101010B 

        ; f f h f * k k k l
        movaps xmm7, xmm4
        mulps xmm7, xmm5

        ; g g g h
        movaps xmm6, xmm2
        movlhps xmm6, xmm3
        shufps xmm6, xmm6, 11010101B

        ; j j l j
        movaps xmm4, xmm1
        movhlps xmm4, xmm3
        shufps xmm4, xmm4, 10001010B

        ; g g g h * j j l j
        mulps xmm4, xmm6

        ; f f h f * k k k l - g g g h * j j l j
        subps xmm7, xmm4

        ; a d a a
        movaps xmm5, xmm0
        movlhps xmm5, xmm3
        shufps xmm5, xmm5, 00001000B

        ; a d a a * (f f h f * k k k l - g g g h * j j l j)
        mulps xmm7, xmm5

        ; i l i i
        movaps xmm5, xmm0
        movhlps xmm5, xmm3
        shufps xmm5, xmm5, 10100010B

        ; g g g h * i l i i
        mulps xmm6, xmm5

        ; e h e e
        movaps xmm4, xmm0
        movlhps xmm4, xmm3
        shufps xmm4, xmm4, 01011101B

        ; k k k l
        movaps xmm5, xmm2
        movhlps xmm5, xmm3
        shufps xmm5, xmm5, 00101010B 

        ; e h e e * k k k l
        mulps xmm5, xmm4

        ; g g g h * i l i i - e h e e * k k k l
        subps xmm6, xmm5

        ; b b d b
        movaps xmm5, xmm1
        movlhps xmm5, xmm3
        shufps xmm5, xmm5, 00100000B

        ; b b d b * (g g g h * i l i i - e h e e * k k k l)
        mulps xmm6, xmm5

        addps xmm7, xmm6

        ; j j l j
        movaps xmm5, xmm1
        movhlps xmm5, xmm3
        shufps xmm5, xmm5, 10001010B

        ; e e h e * j j l j 
        mulps xmm4, xmm5

        ; f f h f
        movaps xmm6, xmm1
        movlhps xmm6, xmm3
        shufps xmm6, xmm6, 01110101B

        ; i l i i
        movaps xmm5, xmm0
        movhlps xmm5, xmm3
        shufps xmm5, xmm5, 10100010B

        ; f f h f * i l i i
        mulps xmm6, xmm5

        ; e h e e * j j l j - f f h f * i l i i
        subps xmm4, xmm6

        ; c c c d
        movaps xmm5, xmm2
        movlhps xmm5, xmm3
        shufps xmm5, xmm5, 10000000B

        ; c c c d * (e h e e * j j l j - f f h f * i l i i)
        mulps xmm4, xmm5

        addps xmm7, xmm4

        macro broadcast xmm3 = xmm7[0]
        divps xmm7, xmm3

        movhlps xmm5, xmm7
        
        movaps xmm4, xmm7
        shufps xmm4, xmm4, 0x55 
        
        movaps xmm6, xmm7
        shufps xmm6, xmm6, 0xFF

        ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta

        pxor xmm3, xmm3
        macro eq128 xmm2 = xmm4
        macro if xmm4 < xmm3 goto _reject_092
        macro if xmm5 < xmm3 goto _reject_092
        addss xmm4, xmm5
        macro if xmm4 > one goto _reject_092

        comiss xmm6, dword [epsilon]
        jc _reject_092
        comiss xmm6, dword [ecx] ;minimum distance
        jnc _reject_092

        ;populate hitpoint structure
        ; t is in xmm6
        
        mov eax, 1
        jmp _accept_092

        _reject_092:
        xor eax, eax
        _accept_092:

        """
    
    return code



import renmas3.switch as proc
import struct

#input
# xmm3 - origin
# xmm4 - direction
# xmm5 - p0
# xmm6 - p1
# xmm7 - p2

#output
# xmm0 = t
# xmm1 = beta
# xmm2 = gamma
# eax = intersection_ocur 0-no , 1-yes

def float2hex(f):
    r = struct.pack('f', f)
    r1 = struct.unpack('I', r)[0]
    return hex(r1)

def ray_triangle_intersection(label, epsilon=0.00005):
    epsilon = float2hex(epsilon)
    if proc.AVX:
        lab = "#CODE\n"
        lab += "global %s:\n" % label
        lab += "mov ecx, %s\n" % epsilon

        code = lab + """
        vsubps xmm0, xmm5, xmm6
        vsubps xmm1, xmm5, xmm7
        vmovaps xmm2, xmm4
        vsubps xmm3, xmm5, xmm3
        mov eax, esp
        and eax, 0xFFFFFFF0

        ; f f h f
        vmovlhps xmm4, xmm1, xmm3
        vpermilps xmm4, xmm4, 01110101B 
        vmovaps oword [eax - 16], xmm4

        ; k k k l
        vmovhlps xmm5, xmm2, xmm3
        vpermilps xmm5, xmm5, 00101010B 
        vmovaps oword [eax - 32], xmm5

        ; f f h f * k k k l
        vmulps xmm7, xmm4, xmm5

        ; g g g h
        vmovlhps xmm6, xmm2, xmm3
        vpermilps xmm6, xmm6, 11010101B 

        ; j j l j
        vmovhlps xmm4, xmm1, xmm3
        vpermilps xmm4, xmm4, 10001010B 
        vmovaps oword [eax - 48], xmm4

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
        vmovaps oword [eax - 64], xmm5

        ; g g g h * i l i i
        vmulps xmm6, xmm6, xmm5

        ; e h e e
        vmovlhps xmm4, xmm0, xmm3
        vpermilps xmm4, xmm4, 01011101B 

        ; k k k l
        vmovaps xmm5, oword [eax - 32]

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
        vmovaps xmm5, oword [eax - 48]

        ; e e h e * j j l j 
        vmulps xmm4, xmm4, xmm5

        ; f f h f
        vmovaps xmm6, oword [eax - 16]

        ; i l i i
        vmovaps xmm5, oword [eax - 64]

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

        ; this is new
        vpcmpeqw xmm1, xmm1, xmm1
        vpslld xmm1, xmm1, 31
        vandps xmm1, xmm1, xmm3
        vxorps xmm1, xmm1, xmm7

        ; xmm0 = gamma
        vpxor xmm2, xmm2, xmm2
        vpermilps xmm0, xmm1, 10101010B 
        vcomiss xmm0, xmm2
        jc _reject_092

        ; xmm1 = beta
        vpermilps xmm1, xmm1, 01010101B 
        vcomiss xmm1, xmm2
        jc _reject_092

        ; end of new
        
        vdivps xmm7, xmm7, xmm3

        vpermilps xmm5, xmm7, 10101010B 
        vpermilps xmm4, xmm7, 01010101B 
        vpermilps xmm6, xmm7, 11111111B 

        ;generate 1.0
        vpcmpeqw xmm3, xmm3, xmm3
        vpslld xmm3, xmm3, 25
        vpsrld xmm3, xmm3, 2

        ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta
        vmovss xmm1, xmm1, xmm4
        vmovss xmm2, xmm2, xmm5
        vaddss xmm4, xmm4, xmm5
        vcomiss xmm4, xmm3
        jnc _reject_092
        vmovd xmm0, ecx
        vcomiss xmm6, xmm0
        jc _reject_092

        vmovss xmm0, xmm0, xmm6
        mov eax, 1
        ret
       
        _reject_092:
        xor eax, eax
        ret
        """
    else:

        lab = "#CODE\n"
        lab += "global %s:\n" % label
        lab += "mov ecx, %s\n" % epsilon

        code = lab + """
            movaps xmm0, xmm5
            subps xmm0, xmm6
            movaps xmm1, xmm5
            subps xmm1, xmm7
            movaps xmm2, xmm4
            subps xmm5, xmm3
            movaps xmm3, xmm5
            mov eax, esp
            and eax, 0xFFFFFFF0

            ; f f h f
            movaps xmm4, xmm1
            movlhps xmm4, xmm3
            shufps xmm4, xmm4, 01110101B
            movaps oword [eax - 16], xmm4

            ; k k k l
            movaps xmm5, xmm2
            movhlps xmm5, xmm3
            shufps xmm5, xmm5, 00101010B 
            movaps oword [eax - 32], xmm5

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
            movaps oword [eax - 48], xmm4

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
            movaps oword [eax - 64], xmm5

            ; g g g h * i l i i
            mulps xmm6, xmm5

            ; e h e e
            movaps xmm4, xmm0
            movlhps xmm4, xmm3
            shufps xmm4, xmm4, 01011101B

            ; k k k l
            movaps xmm5, oword [eax - 32]

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
            movaps xmm5, oword [eax - 48]

            ; e e h e * j j l j 
            mulps xmm4, xmm5

            ; f f h f
            movaps xmm6, oword [eax - 16]

            ; i l i i
            movaps xmm5, oword [eax - 64]

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

            movaps xmm3, xmm7
            shufps xmm3, xmm3, 0x00

            ; this is new
            pcmpeqw xmm1, xmm1
            pslld xmm1, 31
            andps xmm1, xmm3
            xorps xmm1, xmm7

            ; xmm0 = gamma
            pxor xmm2, xmm2
            movhlps xmm0, xmm1
            comiss xmm0, xmm2
            jc _reject_092

            ; xmm1 = beta
            shufps xmm1, xmm1, 0x55 
            comiss xmm1, xmm2
            jc _reject_092

            ; end of new

            divps xmm7, xmm3

            movhlps xmm5, xmm7
            
            movaps xmm4, xmm7
            shufps xmm4, xmm4, 0x55 
            
            movaps xmm6, xmm7
            shufps xmm6, xmm6, 0xFF

            ;generate 1.0
            pcmpeqw xmm3, xmm3
            pslld xmm3, 25
            psrld xmm3, 2

            ; xmm7 = d  xmm6 = td  xmm5 = gamma   xmm4 = beta
            movss xmm1, xmm4
            movss xmm2, xmm5
            addss xmm4, xmm5
            comiss xmm4, xmm3
            jnc _reject_092
            movd xmm0, ecx
            comiss xmm6, xmm0
            jc _reject_092

            movss xmm0, xmm6
            mov eax, 1
            ret
           
            _reject_092:
            xor eax, eax
            ret

        """
    return code



import renmas3.switch as proc

def sqrtss(asm, tokens):
    
    xmm1, dummy, xmm2 = tokens
    if proc.AVX:
        return 'vsqrtss %s,%s,%s\n' % (xmm1, xmm1, xmm2)
    else:
        return 'sqrtss %s,%s\n' % (xmm1, xmm2)


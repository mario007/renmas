import platform
import renmas3.switch as proc

def generate_one(asm, tokens):

    bits = platform.architecture()[0]
    if bits == '64bit':
        xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    else:
        xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7",
                "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14", "xmm15"]
    
    xmm = tokens[0]
    if xmm not in xmm_regs:
        raise ValueError("Xmm register is expected and got ", xmm)

    if proc.AVX:
        line1 = "vpcmpeqw %s, %s, %s\n" % (xmm, xmm, xmm)
        line2 = "vpslld %s, %s, 25\n" % (xmm, xmm)
        line3 =  "vpsrld %s, %s, 2\n" % (xmm, xmm)
    else:
        line1 = "pcmpeqw %s, %s\n" % (xmm, xmm)
        line2 = "pslld %s, 25\n" % xmm
        line3 = "psrld %s, 2\n" % xmm

    return line1 + line2 + line3 


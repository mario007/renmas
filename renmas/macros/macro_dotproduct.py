
from .utils import pre_proces, filter_tokens
import renmas.utils as util

# for SSE2 extra temp register is needed for dot product
txmm = None

def dot_ins(a, b):
    regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

    if b in regs:
        if util.AVX:
            code = ' vdpps ' + a + ', ' + a + ', ' + b + ', 0xf1'
        else:
            if util.SSE41:
                code = " dpps " + a + ', ' + b + ', 0xf1' 
            else:
                code = " movaps " + txmm + ", " + b + "\n"
                code += " mulps " + a + "," + txmm + "\n"
                code += " movhlps " + txmm + "," + a + "\n"
                code += " addps " + a + "," + txmm + "\n"
                code += " pshufd " + txmm + "," + a + ",1\n"
                code += " addss " + a + "," + txmm + "\n"
    else:
        if util.AVX:
            code = ' vdpps ' + a + ', ' + a + ', oword [' + b + '], 0xf1' 
        else:
            if util.SSE41:
                code = ' dpps ' + a + ', oword [' + b + '], 0xf1' 
            else:
                code = " movaps " + txmm + ", oword [" + b + "]\n"
                code += " mulps " + a + "," + txmm + "\n"
                code += " movhlps " + txmm + "," + a + "\n"
                code += " addps " + a + "," + txmm + "\n"
                code += " pshufd " + txmm + "," + a + ",1\n"
                code += " addss " + a + "," + txmm + "\n"

    return code
    
# dot_product xmm0 = xmm0 * xmm
# dot_product xmm3 = xmm4 * d
# dot_product c = a * b
# dot_product xmm3 = a * b

def dot_product(asm, tokens):
    allowed = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    
    tokens, allowed = filter_tokens(tokens, allowed)
    tokens = pre_proces(tokens)
    xmm = allowed[0]
    global txmm
    txmm = allowed[1]
    
    if len(tokens) != 5:  
        print("Wrong number of tokens")
        return "samo da pukne transofrmacija u strojni kod"
    
    regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]


    a, equal, b, mul, c = tokens 

    if txmm == a:
        txmm = allowed[2]

    if util.AVX:
        mov = " vmovaps "
    else:
        mov = " movaps "

    line1 = line2 = line3 = ""
    if b not in regs and c not in regs: # dot_product xmm3 = a * b ili c = a * b
        if a in regs:
            line1 = mov + a + ", oword [" + b +"]"
            line2 = dot_ins(a, c)
        else:
            line1 = mov + xmm + ", oword [" + b +"]"
            line2 = dot_ins(xmm, c)
            line3 = mov + " oword [" + a + "], " + xmm 
    if b in regs and c in regs: 
        if a == b: #xmm1 = xmm1 * xmm3
            line1 = dot_ins(b, c)
        elif a == c:
            line1 = dot_ins(c, b)
        elif a in regs: 
            if util.AVX:
                line1 = " vdpps " + a + "," + b + "," + c + ", 0xf1"
            else:
                line1 = mov + a + ", " + b
                line2 = dot_ins(a, c)
        else:
            if util.AVX:
                line1 = " vdpps " + xmm + "," + b + "," + c + ", 0xf1"
                line2 = mov + " oword[" + a + "], " + xmm
            else:
                line1 = mov + xmm + ", oword [" + b +"]"
                line2 = dot_ins(xmm, c)
                line3 = mov + " oword[" + a + "], " + xmm

    if b in regs and c not in regs:
        if a == b:
            line1 = dot_ins(b, c)
        elif a in regs:
            if util.AVX:
                line1 = " vdpps " + a + "," + b + ", oword [" + c + "], 0xf1"
            else:
                line1 = mov + a + ", " + b
                line2 = dot_ins(a, c)
        else:
            if util.AVX:
                line1 = " vdpps " + xmm + "," + b + ", oword [" + c + "], 0xf1"
                line2 = mov + " oword[" + a + "], " + xmm
            else:
                line1 = mov + xmm + ", oword [" + b +"]"
                line2 = dot_ins(xmm, c)
                line3 = mov + " oword[" + a + "], " + xmm

    if b not in regs and c in regs:
        if a == c:
            line1 = dot_ins(c, b)
        elif a in regs:
            if util.AVX:
                line1 = " vdpps " + a + "," + c + ", oword [" + b + "], 0xf1"
            else:
                line1 = mov + a + ", " + c
                line2 = dot_ins(a, b)
        else:
            if util.AVX:
                line1 = " vdpps " + xmm + "," + c + ", oword [" + b + "], 0xf1"
                line2 = mov + " oword[" + a + "], " + xmm
            else:
                line1 = mov + xmm + ", oword [" + c +"]"
                line2 = dot_ins(xmm, b)
                line3 = mov + " oword[" + a + "], " + xmm


    asm = line1 + "\n" + line2 + "\n" + line3
    return asm



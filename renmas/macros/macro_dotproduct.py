
from .utils import pre_proces, filter_tokens
import renmas.utils as util

ASM_CODE = """
    #DATA

    uint32 x
    float d[4] = 3.4, 5.5, 7.8, 9.9
    float c[4] = 4.1, 3.3, 5.5, 9.9
    float rez[4]

    #CODE
    mov eax, 122 
    macro dot_product rez =   c  * d   
    #END

    """ 

def check_xmm(xmm):
    return xmm in ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

def dot_ins(a, b):
    regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

    if b in regs:
        if util.AVX:
            code = ' vdpps ' + a + ', ' + a + ', ' + b + ', 0xf1'
        else:
            code = " dpps " + a + ', ' + b + ', 0xf1' 
    else:
        if util.AVX:
            code = ' vdpps ' + a + ', ' + a + ', oword [' + b + '], 0xf1' 
        else:
            code = ' dpps ' + a + ', oword [' + b + '], 0xf1' 

    return code
    
# dot_product xmm0 = xmm0 * xmm
# dot_product xmm3 = xmm4 * d
# dot_product c = a * b
# dot_product xmm3 = a * b

def dot_product(tokens):
    allowed = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    
    tokens, allowed = filter_tokens(tokens, allowed)
    tokens = pre_proces(tokens)
    xmm = allowed[0]

    if len(tokens) != 5: #FIXME nije dobro ne podrzava strukture 
        print("Wrong number of tokens")
        return "samo da pukne transofrmacija u strojni kod"
    
    regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]


    a, equal, b, mul, c = tokens 
    if util.AVX:
        mov = " vmovaps "
    else:
        mov = " movaps "

    line1 = line2 = line3 = ""
    if b not in regs and c not in regs: # dot_product xmm3 = a * b ili c = a * b
        if a in regs:
            line1 = mov + a + ", oword [" + b +"]"
            line2 = dot_ins(a, c)
            line3 = ""
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
            line1 = mov + a + ", " + b
            line2 = dot_ins(a, c)
        else:
            line1 = mov + xmm + ", oword [" + b +"]"
            line2 = dot_ins(xmm, c)
            line3 = mov + " oword[" + a + "], " + xmm

    if b in regs and c not in regs:
        if a == b:
            line1 = dot_ins(b, c)
        elif a in regs:
            line1 = mov + a + ", " + b
            line2 = dot_ins(a, c)
        else:
            line1 = mov + xmm + ", oword [" + b +"]"
            line2 = dot_ins(xmm, c)
            line3 = mov + " oword[" + a + "], " + xmm

    if b not in regs and c in regs:
        if a == c:
            line1 = dot_ins(c, b)
        elif a in regs:
            line1 = mov + a + ", " + c
            line2 = dot_ins(a, b)
        else:
            line1 = mov + xmm + ", oword [" + c +"]"
            line2 = dot_ins(xmm, b)
            line3 = mov + " oword[" + a + "], " + xmm


    asm = line1 + "\n" + line2 + "\n" + line3
    return asm


if __name__ == "__main__":

    asm = tdasm.Tdasm()
    asm.register_macro("dot_product", dot_product)
    
    mc = asm.assemble(ASM_CODE)

    run = runtime.Runtime()
    ds = run.load('test', mc)

    run.run("test")

    print(ds["rez"])

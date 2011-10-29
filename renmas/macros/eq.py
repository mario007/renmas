
from .utils import pre_proces, filter_tokens
import renmas.utils as util


xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
def assign128(tok1, tok2, xmm_reg):
    if util.AVX:
        mov = " vmovaps "
    else:
        mov = " movaps "

    line1 = line2 = ""
    if tok1 == tok2: #self assigment to eliminate xmm1=xmm1
        return []
    if tok1 in xmm_regs:
        if tok2 in xmm_regs:
            line1 = mov + tok1 + "," + tok2
        else:
            line1 = mov + tok1 + "," + "oword [" + tok2 + "]"
    else:
        if tok2 in xmm_regs:
            line1 = mov + "oword [" + tok1 + "]," + tok2 
        else:
            line1 = mov + xmm_reg + ", oword [" + tok2 + "] \n" 
            line2 = mov + "oword [" + tok1 + "]," +  xmm_reg

    return (line1, line2) 

def assign32(tok1, tok2, xmm_reg):
    if tok1 == tok2: #self assigment to eliminate xmm1=xmm1
        return [] 

    line1 = line2 = ""
    if tok1 in xmm_regs:
        if tok2 in xmm_regs:
            line1 = " movss " + tok1 + "," + tok2
        else:
            line1 = " movss " + tok1 + "," + "dword [" + tok2 + "]"
    else:
        if tok2 in xmm_regs:
            line1 = " movss " + "dword [" + tok1 + "]," + tok2 
        else:
            line1 = " movss " + xmm_reg + ", dword [" + tok2 + "] \n" 
            line2 = " movss " + "dword [" + tok1 + "]," +  xmm_reg
    return (line1, line2) 

def assign32avx(tok1, tok2, xmm_reg):
    if tok1 == tok2: #self assigment to eliminate xmm1=xmm1
        return ""

    line1 = line2 = ""
    if tok1 in xmm_regs:
        if tok2 in xmm_regs:
            line1 = " vmovss " + tok1 + ',' + tok1 +"," + tok2
        else:
            line1 = " vmovss " + tok1 + "," + "dword [" + tok2 + "]"
    else:
        if tok2 in xmm_regs:
            line1 = " vmovss " + "dword [" + tok1 + "]," + tok2 
        else:
            line1 = " vmovss " + xmm_reg + ", dword [" + tok2 + "] \n" 
            line2 = " vmovss " + "dword [" + tok1 + "]," +  xmm_reg
    return (line1, line2) 


def ins(a, b, operator, size):
    regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

    if b in regs:
        if util.AVX:
            code = operator + a + ', ' + a + ', ' + b 
        else:
            code = operator + a + ', ' + b  
    else:
        if util.AVX:
            code = operator + a + ', ' + a + ', ' + size + ' [' + b + ']' 
        else:
            code = operator + a + ', ' + size + ' [' + b + ']'

    return code

# eq xmm0 = xmm0 * xmm
# eq xmm3 = xmm4 * d
# eq c = a * b
# eq xmm3 = a * b

ar128_sse = {"+": " addps ", "-": " subps ", "*": " mulps ", "/": " divps "}
ar128_avx = {"+": " vaddps ", "-": " vsubps ", "*": " vmulps ", "/": " vdivps "}
ar32_sse = {"+": " addss ", "-": " subss ", "*": " mulss ", "/": " divss "}
ar32_avx = {"+": " vaddss ", "-": " vsubss ", "*": " vmulss ", "/": " vdivss "}

def eq(tokens, size, xmm):
    #allowed = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    
    #tokens, allowed = filter_tokens(tokens, allowed)
    tokens = pre_proces(tokens)
    #xmm = allowed[0]

    if len(tokens) == 3: # assign
        a, equal, b = tokens
        if size == 32:
            if util.AVX:
                return assign32avx(a, b, xmm)
            else:
                return assign32(a, b, xmm)
        elif size == 128:
            return assign128(a, b, xmm)


    if len(tokens) != 5: #FIXME nije dobro ne podrzava strukture 
        print("Wrong number of tokens")
        return None
    
    regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]


    a, equal, b, operator, c = tokens

    if operator in ['-', '/']: order = True #order matter
    else: order = False


    if util.AVX:
        if size == 32:
            mov = " vmovss "
            ar = ar32_avx
            wide = " dword "
        elif size == 128:
            mov = " vmovaps "
            ar = ar128_avx
            wide = " oword "
    else:
        if size == 32:
            mov = " movss "
            ar = ar32_sse
            wide = " dword "
        elif size == 128:
            mov = " movaps "
            ar = ar128_sse
            wide = " oword "

    line1 = line2 = line3 = ""
    if b not in regs and c not in regs: # dot_product xmm3 = a * b ili c = a * b
        if a in regs:
            line1 = mov + a + ", " + wide + " [" + b +"]"
            line2 = ins(a, c, ar[operator], wide)
        else:
            line1 = mov + xmm + ", " + wide + " [" + b +"]"
            line2 = ins(xmm, c, ar[operator], wide)
            line3 = mov + wide + " [" + a + "], " + xmm 
    if b in regs and c in regs:
        if a == b: #xmm1 = xmm1 * xmm3
            line1 = ins(b, c, ar[operator], wide)
        elif a == c: 
            if util.AVX:
                line1 = ar[operator] + a + "," + b + "," + c 
            else:
                if order: # order matter
                    line1 = ins(b, c, ar[operator], wide)
                    line2 = mov + a + ", " + b
                else:
                    line1 = ins(c, b, ar[operator], wide)
        elif a in regs: 
            if util.AVX:
                line1 = ar[operator] + a + "," + b + "," + c 
            else:
                line1 = mov + a + ", " + b
                line2 = ins(a, c, ar[operator], wide)
        else:
            if util.AVX:
                line1 = ar[operator] + xmm + "," + b + "," + c 
                line2 = mov + wide + " [" + a + "], " + xmm
            else:
                line1 = mov + xmm + ", " + b
                line2 = ins(xmm, c, ar[operator], wide)
                line3 = mov + wide + "[" + a + "], " + xmm

    if b in regs and c not in regs:
        if a == b:
            line1 = ins(b, c, ar[operator], wide)
        elif a in regs:
            if util.AVX:
                line1 = ar[operator] + a + "," + b + ", " + wide + " [" + c + "]"
            else:
                line1 = mov + a + ", " + b
                line2 = ins(a, c, ar[operator], wide)
        else:
            if util.AVX:
                line1 = ar[operator] + xmm + "," + b + ", " + wide + " [" + c + "]"
                line2 = mov + wide + "[" + a + "], " + xmm
            else:
                if size == 32:
                    if util.AVX:
                        line1 = mov + xmm + "," + xmm + ", " +  b 
                    else:
                        line1 = mov + xmm + ", " +  b 
                else:
                    line1 = mov + xmm + ", " +  b 
                line2 = ins(xmm, c, ar[operator], wide)
                line3 = mov + wide + "[" + a + "], " + xmm

    if b not in regs and c in regs:
        if a == c:
            if order: #order matter
                line1 = mov + xmm + ", " + wide + " [" + b +"]"
                line2 = ins(xmm, c, ar[operator], wide)
                if size == 32:
                    if util.AVX:
                        line3 = mov + a + "," + a + ", " + xmm 
                    else:
                        line3 = mov + a + "," + xmm 
                else:
                    line3 = mov + a + ", " + xmm 
            else:
                line1 = ins(c, b, ar[operator], wide)
        elif a in regs:
            if util.AVX:
                if order:
                    line1 = mov + xmm + ", " + wide + " [" + b +"]"
                    line2 = ar[operator] + a + "," + xmm + ", " +  c 
                else:
                    line1 = ar[operator] + a + "," + c + ", " + wide + " [" + b + "]"
            else:
                if order:
                    line1 = mov + xmm + ", " + wide + " [" + b +"]"
                    line2 = ins(xmm, c, ar[operator], wide)
                    line3 = mov + a + ", " + xmm
                else:
                    line1 = mov + a + ", " + c
                    line2 = ins(a, b, ar[operator], wide)
        else:
            if util.AVX:
                if order:
                    line1 = mov + xmm + ", " + wide + " [" + b +"]"
                    line2 = ar[operator] + xmm + "," + xmm + ", " + c
                    line3 = mov + wide + "[" + a + "], " + xmm
                else:
                    line1 = ar[operator] + xmm + "," + c + ", " + wide + " [" + b + "]"
                    line2 = mov + wide + "[" + a + "], " + xmm
            else:
                line1 = mov + xmm + ", " + wide + " [" + b +"]"
                line2 = ins(xmm, c, ar[operator], wide)
                line3 = mov + wide + "[" + a + "], " + xmm


    asm = (line1, line2, line3)
    return asm

def eq128(asm, tokens):
    allowed = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    tokens, allowed = filter_tokens(tokens, allowed)
    xmm = allowed[0]

    lst_inst = eq(tokens, 128, xmm)
    code = ""
    for l in lst_inst:
        code += l + "\n" 
    return code

def eq32(asm, tokens):
    allowed = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    tokens, allowed = filter_tokens(tokens, allowed)
    xmm = allowed[0]

    lst_inst = eq(tokens, 32, xmm)
    code = ""
    for l in lst_inst:
        code += l + "\n" 
    return code


def eq_mix(tokens, art1, art2):

    xmm_regs1 = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    # slplit in two expressions
    tok1 = tokens[0:tokens.index(",")]
    tok2 = tokens[tokens.index(",")+1:]

    new_toks1, allowed_regs = filter_tokens(tok1, xmm_regs1)
    new_toks2, allowed_regs = filter_tokens(tok2, allowed_regs)

    xmm1 = allowed_regs[0]
    xmm2 = allowed_regs[1]

    if new_toks1[0] == xmm2:
        xmm1, xmm2 = xmm2, xmm1

    if new_toks2[0] == xmm1:
        xmm1, xmm2 = xmm2, xmm1

    
    if art1 == 128:
        lst_inst1 = eq(new_toks1, 128, xmm1)
    elif art1 == 32:
        lst_inst1 = eq(new_toks1, 32, xmm1)
        
    if art2 == 128:
        lst_inst2 = eq(new_toks2, 128, xmm2)
    elif art2 == 32:
        lst_inst2 = eq(new_toks2, 32, xmm2)

    code = ""
    if len(lst_inst1) <= len(lst_inst2):
        for l in range(len(lst_inst1)):
            code += lst_inst1[l] + "\n"
            code += lst_inst2[l] + "\n"
        for l in range(len(lst_inst1), len(lst_inst2)):
            code += lst_inst2[l] + "\n"
    else:
        for l in range(len(lst_inst2)):
            code += lst_inst1[l] + "\n"
            code += lst_inst2[l] + "\n"
        for l in range(len(lst_inst2), len(lst_inst1)):
            code += lst_inst1[l] + "\n"

    return code

def eq128_32(asm, tokens):
    return eq_mix(tokens, 128, 32)

def eq32_128(asm, tokens):
    return eq_mix(tokens, 32, 128)

def eq128_128(asm, tokens):
    return eq_mix(tokens, 128, 128)

def eq32_32(asm, tokens):
    return eq_mix(tokens, 32, 32)


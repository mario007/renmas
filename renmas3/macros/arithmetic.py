
import renmas3.switch as proc
from .shared import combine_tokens, select_registers 

xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

def assign128(tok1, tok2, xmm_reg):
    if proc.AVX:
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
        return []

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

def _dest_reg(token, allowed):
    if token in xmm_regs: return token
    if len(allowed) == 0: raise ValueError('Missing allowed register!')
    return allowed[0]

def _assign32(tokens, tmp_reg):
    a, equal, b = tokens
    if proc.AVX:
        return assign32avx(a, b, tmp_reg)
    else:
        return assign32(a, b, tmp_reg)

def _assign128(tokens, tmp_reg):
    a, equal, b = tokens
    return assign128(a, b, tmp_reg)

def _return_code(instructions):
    code = ""
    for l in instructions:
        code += l + "\n" 
    return code

def preform_operation32(dest_reg, operation, source):
    ar32_sse = {"+": " addss ", "-": " subss ", "*": " mulss ", "/": " divss " }
    ar32_avx = {"+": " vaddss ", "-": " vsubss ", "*": " vmulss ", "/": " vdivss "}
    if source in xmm_regs:
        if proc.AVX:
            line = ar32_avx[operation] + dest_reg + "," + dest_reg + ',' + source
        else:
            line = ar32_sse[operation] + dest_reg + ',' + source
    else:
        if proc.AVX:
            line = ar32_avx[operation] + dest_reg + ',' + dest_reg + ',' + ' dword[' + source + ']'
        else:
            line = ar32_sse[operation] + dest_reg + ',' + ' dword[' + source + ']'
    return (line,)

def preform_operation128(dest_reg, operation, source):
    ar128_sse = {"+": " addps ", "-": " subps ", "*": " mulps ", "/": " divps " }
    ar128_avx = {"+": " vaddps ", "-": " vsubps ", "*": " vmulps ", "/": " vdivps " }

    if source in xmm_regs:
        if proc.AVX:
            line = ar128_avx[operation] + dest_reg + "," + dest_reg + ',' + source
        else:
            line = ar128_sse[operation] + dest_reg + ',' + source
    else:
        if proc.AVX:
            line = ar128_avx[operation] + dest_reg + ',' + dest_reg + ',' + ' oword[' + source + ']'
        else:
            line = ar128_sse[operation] + dest_reg + ',' + ' oword[' + source + ']'
    return (line,)

def arithmetic(tokens, size):
    tokens, allowed = select_registers(tokens)
    dest_reg = _dest_reg(tokens[0], allowed)
    tokens = combine_tokens(tokens)

    if len(tokens) == 3: # assignment
        if size == 128:
            lines = _assign128(tokens, dest_reg)
        else:
            lines = _assign32(tokens, dest_reg)
        return _return_code(lines)

    #Phase1 -  move token2 to dest reg - use assignment
    toks = (dest_reg, '=', tokens[2])
    if size == 128:
        lines = _assign128(toks, dest_reg)
    else:
        lines = _assign32(toks, dest_reg) #AVX fist two can add without assigment TODO

    #Phase2 - preform operation on every next token 
    for idx in range(3, len(tokens), 2):
        operation = tokens[idx]
        tok = tokens[idx+1]
        if size == 128:
            lines += preform_operation128(dest_reg, operation, tok)
        else:
            lines += preform_operation32(dest_reg, operation, tok)

    #Store result
    if dest_reg != tokens[0]:
        toks = (tokens[0], '=', dest_reg)
        if size == 128:
            lines += _assign128(toks, dest_reg)
        else:
            lines += _assign32(toks, dest_reg)

    return _return_code(lines)

def arithmetic32(asm, tokens):
    return arithmetic(tokens, 32)


def arithmetic128(asm, tokens):
    return arithmetic(tokens, 128)


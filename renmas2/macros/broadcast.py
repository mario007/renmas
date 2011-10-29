
import renmas2.switch as proc
from .shared import combine_tokens, select_registers 

def broadcast(asm, tokens):

    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

    rb = tokens.pop()
    idx = tokens.pop()
    lb = tokens.pop()
    tokens = combine_tokens(tokens)
    
    # macro broadcast xmm4 = xmm3(2)
    # macro broadcast xmm4 = xmm4[2]
    # macro broadcast xmm2 = eax.ray.dir[0]
    if len(tokens) != 3:
        raise ValueError('Wrong number of operand in broadcast macro.')

    op1, eq, op2 = tokens
    if op1 not in xmm_regs:
        raise ValueError('First operand must be xmm register.')

    comp = {"0":"0x00", "1":"0x55", "2":"0xAA", "3":"0xFF"}
    line1 = line2 = ""
    if op2 in xmm_regs:
        if op1 == op2:
            if proc.AVX:
                line1 = " vshufps " + op1 + ", " + op1 + ", " + op1 + ", " + comp[idx]  
            else:
                line1 = " shufps " + op1 + ", " + op1 + ", " + comp[idx]  
        else:
            if proc.AVX:
                line1 = " vshufps " + op1 + ", " + op2 + ", " + op2 + ", " + comp[idx]
            else:
                line1 = " movaps " + op1 + ", " + op2
                line2 = " shufps " + op1 + ", " + op1 + ", " + comp[idx]  
    else:
        if proc.AVX:
            line1 = " vmovaps " + op1 + ", oword [" + op2 + "]"
            line1 = " vshufps " + op1 + ", " + op1 + ", " + op1 + ", " + comp[idx]
        else:
            line1 = " movaps " + op1 + ", oword [" + op2 + "]"
            line2 = " shufps " + op1 + ", " + op1 + ", " + comp[idx]  


    return line1 + "\n" + line2 + "\n"


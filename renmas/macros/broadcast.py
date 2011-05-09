
from .utils import pre_proces, filter_tokens
import renmas.utils as util

def broadcast(tokens):

    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

    rb = tokens.pop()
    idx = tokens.pop()
    lb = tokens.pop()
    tokens = pre_proces(tokens)
    
    # macro broadcast xmm4 = xmm3(2)
    # macro broadcast xmm4 = xmm4[2]
    # macro broadcast xmm2 = eax.ray.dir[0]
    if len(tokens) != 3:
        print("Error! Wrong number of operand in broadcast macro.")
        print(tokens)
        return None

    op1, eq, op2 = tokens
    if op1 not in xmm_regs:
        print("First operand must be xmm register.")
        return None

    comp = {"0":"0x00", "1":"0x55", "2":"0xAA", "3":"FF"}
    line1 = line2 = ""
    if op2 in xmm_regs:
        if op1 == op2:
            if util.AVX:
                line1 = " vshufps " + op1 + ", " + op1 + ", " + op1 + ", " + comp[idx]  
            else:
                line1 = " shufps " + op1 + ", " + op1 + ", " + comp[idx]  
        else:
            if util.AVX:
                line1 = " vshufps " + op1 + ", " + op2 + ", " + op2 + ", " + comp[idx]
            else:
                line1 = " movaps " + op1 + ", " + op2
                line2 = " shufps " + op1 + ", " + op1 + ", " + comp[idx]  
    else:
        if util.AVX:
            line1 = " vmovaps " + op1 + ", oword [" + op2 + "]"
            line1 = " vshufps " + op1 + ", " + op1 + ", " + op1 + ", " + comp[idx]
        else:
            line1 = " movaps " + op1 + ", oword [" + op2 + "]"
            line2 = " shufps " + op1 + ", " + op1 + ", " + comp[idx]  


    return line1 + "\n" + line2 + "\n"


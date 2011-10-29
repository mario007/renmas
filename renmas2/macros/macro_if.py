
import renmas2.switch as proc
from .shared import combine_tokens, select_registers 

def macro_if(asm, tokens):
    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    # remove last two tokens goto and label
    label = tokens.pop()
    dummy_goto = tokens.pop()
    tokens = combine_tokens(tokens)
    if len(tokens) != 3:
        raise ValueError('Wrong number of operand in IF macro!')
    
    op1, eq, op2 = tokens
    if op1 not in xmm_regs:
        raise ValueError('First operand must be xmm register.')

    if proc.AVX:
        comiss = " vcomiss "
    else:
        comiss = " comiss "

    if op2 in xmm_regs:
        line1 = comiss + op1 + "," + op2 
    else:
        line1 = comiss + op1 + ", dword [" + op2  + "]"  

    if eq == "<":
        line2 = "jc " + label
    elif eq == ">":
        line2 = "jnc " + label
    else:
        raise ValueError('Error! Only <> are allowed!')

    asm = line1 + "\n" + line2 + "\n" 
    return asm


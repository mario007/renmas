

from .utils import pre_proces, filter_tokens
import renmas.utils as util

def macro_if(asm, tokens):
    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    # remove last two tokens goto and label
    label = tokens.pop()
    dummy_goto = tokens.pop()
    tokens = pre_proces(tokens)
    if len(tokens) != 3:
        print("Error! Wronk number of operand in if macro.")
        return
    
    op1, eq, op2 = tokens
    if op1 not in xmm_regs:
        print("First operand must be xmm register.")
        return

    if util.AVX:
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
        print("Error! <> are allowed.")
        return

    asm = line1 + "\n" + line2 + "\n" 
    return asm

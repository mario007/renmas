
from tdasm import Tdasm, Runtime
from .utils import pre_proces, filter_tokens
import renmas.utils as util

ASM_CODE = """
    #DATA
    float v1[4] = 2.0, 4.0, 2.0, 2.0
    float v2[4] = 3.0, 1.0, 5.0, 2.0
    float v3[4] = 5.0, 5.0, 5.0, 5.0
    float rez[4]

    #CODE
    macro arth128 xmm5 = v1 
    macro arth128 xmm1 = xmm5 
    macro arth128 xmm4 = xmm5 - xmm1 * xmm5 {xmm0, xmm3} 
    macro arth128 rez = xmm4 
    
    #END
"""

xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
reg32 = ["eax", "ebx", "ecx", "edx", "edx", "esi", "esp", "ebx"]
operators = ["+", "-", "*", "/", "="]

precedance = {"+": 10, "-": 10, "*": 20, "/": 20 } 

arth_128_sse = {"+": " addps ", "-": " subps ", "*": " mulps ", "/": " divps "}
arth_32_sse = {"+": " addss ", "-": " subss ", "*": " mulss ", "/": " divss "}
arth_128_avx = {"+": " vaddps ", "-": " vsubps ", "*": " vmulps ", "/": " vdivps "}
arth_32_avx = {"+": " vaddss ", "-": " vsubss ", "*": " vmulss ", "/": " vdivss "}


# return list of instructions
# limitations of 3 operands if *, / and +,- are mix

def gen_float_avx_32(lst_op, size = " dword ", mov=" vmovss ", arth=arth_32_avx, xmms=["xmm0", "xmm1"]):
    curr_acum = xmms[0]
    curr_acum1 = xmms[1]
    
    curr_name = ""
    lst_inst = []
    for op in lst_op:
        if curr_name == "": #we don't yet have intermediate result
            v1 , operator , v2 = op
            if v1 in xmm_regs: 
                if curr_acum != v1:
                    lst_inst.append(mov + curr_acum + "," + curr_acum + ',' + v1)
            else:
                lst_inst.append(mov + curr_acum + "," + size + " [ " + v1 + "]")

            if v2 in xmm_regs:
                lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + v2)
            else:
                lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + size + "[ " + v2 + "]")

            curr_name = v1 + v2
        else:
            v1 , operator , v2 = op
            if v1 == curr_name:
                if v2 in xmm_regs:
                    lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + v2)
                else:
                    lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + size + " [ " + v2 + "]")

                curr_name += v2
            else:
                if v1 in xmm_regs: 
                    lst_inst.append(mov + curr_acum1 + ',' + curr_acum1 + "," + v1)
                else:
                    lst_inst.append(mov + curr_acum1 + "," + size + "[ " + v1 + "]")

                lst_inst.append(arth[operator] + curr_acum1 + ',' + curr_acum1 + "," + curr_acum)

                curr_acum, curr_acum1 = curr_acum1, curr_acum

                curr_name += v1
            
    return (lst_inst, curr_acum)

def gen_float_avx_128(lst_op, size = " oword ", mov=" vmovaps ", arth=arth_128_avx, xmms=["xmm0", "xmm1"]):
    curr_acum = xmms[0]
    curr_acum1 = xmms[1]
    
    curr_name = ""
    lst_inst = []
    for op in lst_op:
        if curr_name == "": #we don't yet have intermediate result
            v1 , operator , v2 = op
            if v1 in xmm_regs: 
                if curr_acum != v1:
                    lst_inst.append(mov + curr_acum + "," + v1)
            else:
                lst_inst.append(mov + curr_acum + "," + size + " [ " + v1 + "]")

            if v2 in xmm_regs:
                lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + v2)
            else:
                lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + size + "[ " + v2 + "]")

            curr_name = v1 + v2
        else:
            v1 , operator , v2 = op
            if v1 == curr_name:
                if v2 in xmm_regs:
                    lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + v2)
                else:
                    lst_inst.append(arth[operator] + curr_acum + "," + curr_acum + ',' + size + " [ " + v2 + "]")

                curr_name += v2
            else:
                if v1 in xmm_regs: 
                    lst_inst.append(mov + curr_acum1 + ',' + v1)
                else:
                    lst_inst.append(mov + curr_acum1 + "," + size + "[ " + v1 + "]")

                lst_inst.append(arth[operator] + curr_acum1 + ',' + curr_acum1 + "," + curr_acum)

                curr_acum, curr_acum1 = curr_acum1, curr_acum

                curr_name += v1
            
    return (lst_inst, curr_acum)

def gen_float(lst_op, size = " oword ", mov=" movaps ", arth=arth_128_sse, xmms=["xmm0", "xmm1"]):
    curr_acum = xmms[0]
    curr_acum1 = xmms[1]
    
    curr_name = ""
    lst_inst = []
    for op in lst_op:
        if curr_name == "": #we don't yet have intermediate result
            v1 , operator , v2 = op
            if v1 in xmm_regs: 
                if curr_acum != v1:
                    lst_inst.append(mov + curr_acum + "," + v1)
            else:
                lst_inst.append(mov + curr_acum + "," + size + " [ " + v1 + "]")

            if v2 in xmm_regs:
                lst_inst.append(arth[operator] + curr_acum + "," + v2)
            else:
                lst_inst.append(arth[operator] + curr_acum + "," + size + "[ " + v2 + "]")

            curr_name = v1 + v2
        else:
            v1 , operator , v2 = op
            if v1 == curr_name:
                if v2 in xmm_regs:
                    lst_inst.append(arth[operator] + curr_acum + "," + v2)
                else:
                    lst_inst.append(arth[operator] + curr_acum + "," + size + " [ " + v2 + "]")

                curr_name += v2
            else:
                if v1 in xmm_regs: 
                    lst_inst.append(mov + curr_acum1 + "," + v1)
                else:
                    lst_inst.append(mov + curr_acum1 + "," + size + "[ " + v1 + "]")

                lst_inst.append(arth[operator] + curr_acum1 + "," + curr_acum)

                curr_acum, curr_acum1 = curr_acum1, curr_acum

                curr_name += v1
            
    return (lst_inst, curr_acum)

def assign128(tok1, tok2, xmm_reg):
    if util.AVX:
        mov = " vmovaps "
    else:
        mov = " movaps "

    if tok1 == tok2: #self assigment to eliminate xmm1=xmm1
        return ""
    if tok1 in xmm_regs:
        if tok2 in xmm_regs:
            asign = mov + tok1 + "," + tok2
        else:
            asign = mov + tok1 + "," + "oword [" + tok2 + "]"
    else:
        if tok2 in xmm_regs:
            asign = mov + "oword [" + tok1 + "]," + tok2 
        else:
            asign = mov + xmm_reg + ", oword [" + tok2 + "] \n" 
            asign += mov + "oword [" + tok1 + "]," +  xmm_reg
    return asign

def assign32(tok1, tok2, xmm_reg):
    if tok1 == tok2: #self assigment to eliminate xmm1=xmm1
        return ""
    if tok1 in xmm_regs:
        if tok2 in xmm_regs:
            asign = " movss " + tok1 + "," + tok2
        else:
            asign = " movss " + tok1 + "," + "dword [" + tok2 + "]"
    else:
        if tok2 in xmm_regs:
            asign = " movss " + "dword [" + tok1 + "]," + tok2 
        else:
            asign = " movss " + xmm_reg + ", dword [" + tok2 + "] \n" 
            asign += " movss " + "dword [" + tok1 + "]," +  xmm_reg
    return asign

def assign32avx(tok1, tok2, xmm_reg):
    if tok1 == tok2: #self assigment to eliminate xmm1=xmm1
        return ""
    if tok1 in xmm_regs:
        if tok2 in xmm_regs:
            asign = " vmovss " + tok1 + ',' + tok1 +"," + tok2
        else:
            asign = " vmovss " + tok1 + "," + "dword [" + tok2 + "]"
    else:
        if tok2 in xmm_regs:
            asign = " vmovss " + "dword [" + tok1 + "]," + tok2 
        else:
            asign = " vmovss " + xmm_reg + ", dword [" + tok2 + "] \n" 
            asign += " vmovss " + "dword [" + tok1 + "]," +  xmm_reg
    return asign

def gen_float128(lst_operations, allowed_regs):
    return gen_float(lst_operations, " oword ", " movaps ", arth_128_sse, allowed_regs)
   
def gen_float32(lst_operations, allowed_regs):
    return gen_float(lst_operations, " dword ", " movss ", arth_32_sse, allowed_regs)

def gen_float128avx(lst_operations, allowed_regs):
    return gen_float_avx_128(lst_operations, " oword ", " vmovaps ", arth_128_avx, allowed_regs)
   
def gen_float32avx(lst_operations, allowed_regs):
    return gen_float_avx_32(lst_operations, " dword ", " vmovss ", arth_32_avx, allowed_regs)


# whith curly braces forbid using some of register {xmm0}
def arth(tokens, assign, gen_inst, allowed_regs):
    op_stack = []
    var_stack = []
        
    tokens = pre_proces(tokens)
    new_tokens = tokens[2:]
    lst_operations = []
    for t in new_tokens:
        if t in operators:
            if len(op_stack) > 0:
                if precedance[t] > precedance[op_stack[-1]]:
                    op_stack.append(t)
                else: # primjeni operator
                    while True: 
                        if len(op_stack) == 0:
                            break
                        if precedance[t] <= precedance[op_stack[-1]]:
                            var2 = var_stack.pop()
                            var1 = var_stack.pop()
                            op1 = op_stack.pop()
                            lst_operations.append((var1, op1, var2))
                            var_stack.append(var1 + var2)
                        else:
                            break
                    op_stack.append(t)
            else:
                op_stack.append(t)
        else:
            var_stack.append(t)

    while len(op_stack) > 0:
        var2 = var_stack.pop()
        var1 = var_stack.pop()
        op1 = op_stack.pop()
        lst_operations.append((var1, op1, var2))
        var_stack.append(var1 + var2)


    if tokens[0] in allowed_regs: #hint for recomended acumulator
        allowed_regs.remove(tokens[0])
        allowed_regs.insert(0, tokens[0])

    xmm_reg = allowed_regs[0]
    if len(lst_operations) == 0: #just assigment
        lst_inst = []
        lst_inst.append(assign(tokens[0], tokens[2], xmm_reg))
    else:
        lst_inst, acum = gen_inst(lst_operations, allowed_regs)
        if acum != tokens[0]:
            lst_inst.append(assign(tokens[0], acum, None))

    return lst_inst 
    
def arth128(tokens):
    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    new_toks, allowed_regs = filter_tokens(tokens, xmm_regs)
    if util.AVX:
        lst_inst = arth(new_toks, assign128, gen_float128avx, allowed_regs)
    else:
        lst_inst = arth(new_toks, assign128, gen_float128, allowed_regs)

    code = ""
    for l in lst_inst:
        code += l + "\n" 
    return code

def arth32(tokens):
    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    new_toks, allowed_regs = filter_tokens(tokens, xmm_regs)
    if util.AVX:
        lst_inst = arth(new_toks, assign32avx, gen_float32avx, allowed_regs)
    else:
        lst_inst = arth(new_toks, assign32, gen_float32, allowed_regs)

    code = ""
    for l in lst_inst:
        code += l + "\n" 
    return code


def arth_mix(tokens, art1, art2):
    xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
    # slplit in two expressions
    tok1 = tokens[0:tokens.index(",")]
    tok2 = tokens[tokens.index(",")+1:]

    new_toks1, allowed_regs = filter_tokens(tok1, xmm_regs)
    new_toks2, allowed_regs = filter_tokens(tok2, allowed_regs)

    allowed1 = allowed_regs[0:2]
    allowed2 = allowed_regs[2:]
    if new_toks1[0] in allowed2:
        allowed2.remove(new_toks1[0])
        x = allowed1.pop()
        allowed1.insert(0, new_toks1[0])
        allowed2.append(x)

    if new_toks2[0] in allowed1:
        allowed1.remove(new_toks2[0])
        x = allowed2.pop()
        allowed2.insert(0, new_toks2[0])
        allowed1.append(x)

    if art1 == 128:
        if util.AVX:
            lst_inst1 = arth(new_toks1, assign128, gen_float128avx, allowed1)
        else:
            lst_inst1 = arth(new_toks1, assign128, gen_float128, allowed1)
    elif art1 == 32:
        if util.AVX:
            lst_inst1 = arth(new_toks1, assign32avx, gen_float32avx, allowed1)
        else:
            lst_inst1 = arth(new_toks1, assign32, gen_float32, allowed1)

    if art2 == 128:
        if util.AVX:
            lst_inst2 = arth(new_toks2, assign128, gen_float128avx, allowed2)
        else:
            lst_inst2 = arth(new_toks2, assign128, gen_float128, allowed2)
    elif art2 == 32:
        if util.AVX:
            lst_inst2 = arth(new_toks2, assign32avx, gen_float32avx, allowed2)
        else:
            lst_inst2 = arth(new_toks2, assign32, gen_float32, allowed2)

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

def arth128_32(tokens):
    return arth_mix(tokens, 128, 32)

def arth32_128(tokens):
    return arth_mix(tokens, 32, 128)

def arth128_128(tokens):
    return arth_mix(tokens, 128, 128)

def arth32_32(tokens):
    return arth_mix(tokens, 32, 32)

if __name__ == "__main__":
    asm = Tdasm()
    asm.register_macro("arth128", arth128)
    asm.register_macro("arth32", arth32)
    mc = asm.assemble(ASM_CODE)

    run = Runtime()
    ds = run.load("test", mc)
    run.run("test")

    print(ds["rez"])


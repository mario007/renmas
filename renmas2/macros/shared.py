
def gen(tokens):
    for t in tokens:
        yield t

def make_gen(tokens):
    mk = gen(tokens)
    def f():
        return next(mk)
    return f

xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]

# solve structure problem(combine multiple tokens in one)  eax.ray.direction  ray.direction
def combine_tokens(tokens):
    operators = ["+", "-", "*", "/", "=", "<", ">"]
    reg32 = ["eax", "ebx", "ecx", "edx", "edx", "esi", "esp", "ebx"]
    next_token = make_gen(tokens)
    lst = [] 
    while True:
        try:
            r = None 
            cur_var = ""
            tok = next_token()
            if tok in xmm_regs or tok in operators:
                lst.append(tok)
                continue

            if tok in reg32:
                r = tok
            else:
                cur_var = tok

            while True:
                tok2 = next_token()
                if tok2 == ".":
                    if cur_var != "":
                        cur_var += "."
                elif tok2 in operators:
                    if r is not None:
                        if cur_var == "":
                            lst.append(r)
                        else:
                            lst.append(r +  "+" + cur_var)
                    else:
                        lst.append(cur_var)
                    lst.append(tok2)
                    break
                else:
                    cur_var += tok2

        except StopIteration:
            if r is not None:
                if cur_var == "":
                    lst.append(r)
                else:
                    lst.append(r +  "+" + cur_var)
            else:
                if cur_var != "":
                    lst.append(cur_var)
            break

    return lst


#remove '{}' from tokens and select temp registers for intermediate results
def select_registers(tokens):
    tok2 = [tokens[0]] 
    in_curly = False
    allowed_regs = []
    for r in tokens[1:]:
        if r == "{": in_curly = True
        if r == "}": 
            in_curly = False
            continue         
        if in_curly: 
            if r in xmm_regs: allowed_regs.append(r)
            continue
        tok2.append(r)
    return (tok2, allowed_regs)




def gen(tokens):
    for t in tokens:
        yield t

def make_gen(tokens):
    mk = gen(tokens)
    def f():
        return next(mk)
    return f

xmm_regs = ["xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]
operators = ["+", "-", "*", "/", "=", "<", ">"]
reg32 = ["eax", "ebx", "ecx", "edx", "edx", "esi", "esp", "ebx"]

# solve structure problem(combine multiple tokens in one)  eax.ray.direction  ray.direction
def pre_proces(tokens):
    lst = []
    next_token = make_gen(tokens)
    while True:
        try:
            r = None 
            cur_var = ""

            tok = next_token()
            if tok in xmm_regs:
                lst.append(tok)
                continue
            if tok in operators:
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

# remove ocupied xmm_regs from allowed registers
# also split expresion in two list if we have two expersions
def filter_tokens(tokens, allowed_regs):
    tok2 = []
    in_curly = False
    
    tok2.append(tokens[0])
    
    for r in tokens[1:]:

        if r in allowed_regs:
            allowed_regs.remove(r)
        if r == "{": in_curly = True
        if r == "}": 
            in_curly = False
            continue         

        if in_curly: continue
        tok2.append(r)
    return (tok2, allowed_regs)


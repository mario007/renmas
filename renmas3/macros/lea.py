
import platform

def lea(asm, tokens):

    reg32 = ["eax", "ebx", "ecx", "edx", "edx", "esi", "esp", "ebx"]
    reg64 = ["rax", "rbx", "rcx", "rdx", "rdx", "rsi", "rsp", "rbx"]

    bits = platform.architecture()[0]
    code = 'lea '

    for t in tokens:
        tok = t
        if bits == '64bit':
            if tok in reg32:
                tok = 'r' + tok[1:] 
            if tok == 'dword':
                tok = 'qword'
        else:
            if tok in reg64:
                tok = 'e' + tok[1:]
            if tok == 'qword':
                tok = 'dword'
        code += tok

    return code


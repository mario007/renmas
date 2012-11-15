
import platform

def _push_and_pop(asm, tokens, cmd):
    bits = platform.architecture()[0]

    reg = tokens[0]
    general32 = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    general64 = ['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax']
    
    if bits == '64bit' and reg in general32:
        reg = 'r' + reg[1:] 
    elif reg in general64:
        reg = 'e' + reg[1:]

    code = "%s %s\n" % (cmd, reg)
    return code

def push(asm, tokens):
    return _push_and_pop(asm, tokens, 'push')

def pop(asm, tokens):
    return _push_and_pop(asm, tokens, 'pop')


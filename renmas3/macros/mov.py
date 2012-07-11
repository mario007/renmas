import platform

# macro to handle mov eax, var 32-bit and 64-bit handling
# example: macro mov eax, mesh1
# or macro mov eax, miro

def mov(asm, tokens):

    bits = platform.architecture()[0]

    reg, comma, var = tokens

    reg32 = ["eax", "ebx", "ecx", "edx", "edx", "esi", "esp", "ebx"]

    reg64 = ["rax", "rbx", "rcx", "rdx", "rdx", "rsi", "rsp", "rbx"]

    if bits == '64bit':
        if reg in reg32:
            return 'mov r' + reg[1:] + ',' + var
        else:
            return 'mov ' + reg + ',' + var
    else:
        if reg in reg64:
            return 'mov e' + reg[1:] + ',' + var
        else:
            return 'mov ' + reg + ',' + var


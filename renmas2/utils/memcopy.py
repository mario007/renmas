
from tdasm import Tdasm, Runtime
import platform


bits = platform.architecture()[0]
if bits == '64bit':
    MEMCPY = """
        #DATA
        uint64 sa, da, n

        #CODE
        mov rcx, qword [n]
        mov rsi, qword [sa] 
        mov rdi, qword [da]
        rep movs byte [rdi], byte [rsi]

        #END
    """
else:
    MEMCPY = """
        #DATA
        uint32 sa, da, n

        #CODE
        mov ecx, dword [n]
        mov esi, dword [sa] 
        mov edi, dword [da]
        rep movs byte [edi], byte [esi]

        #END
    """

asm = Tdasm()
m = asm.assemble(MEMCPY)
run = Runtime()
data_section = run.load("memcpy", m)

def memcpy(da, sa, n):
    data_section["da"] = da
    data_section["sa"] = sa
    data_section["n"] = n
    run.run("memcpy")


import platform
from tdasm import Tdasm, Runtime

def _memcpy_code():
    bits = platform.architecture()[0]
    if bits == '64bit':
        code = """
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
        code = """
            #DATA
            uint32 sa, da, n

            #CODE
            mov ecx, dword [n]
            mov esi, dword [sa] 
            mov edi, dword [da]
            rep movs byte [edi], byte [esi]

            #END
        """
    return code 

_mc = Tdasm().assemble(_memcpy_code())
_runtime = Runtime()
_data_section = _runtime.load("memcpy", _mc)

def memcpy(da, sa, n):
    _data_section["da"] = da
    _data_section["sa"] = sa
    _data_section["n"] = n
    _runtime.run("memcpy")


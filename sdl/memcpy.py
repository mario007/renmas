import platform
from tdasm import translate, Runtime

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

bits = platform.architecture()[0]
if bits == '64bit':
    _mc = translate(_memcpy_code(), ia32=False)
else:
    _mc = translate(_memcpy_code(), ia32=True)

_runtime = Runtime()
_data_section = _runtime.load("memcpy", _mc)

def memcpy(da, sa, n):
    """
        Copy n bytes form source address(sa) to destination address(da).
    """
    _data_section["da"] = da
    _data_section["sa"] = sa
    _data_section["n"] = n
    _runtime.run("memcpy")


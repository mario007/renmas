
from tdasm import Tdasm
from renmas.core import AsmStructures


asm = Tdasm()
AVX = asm.avx_supported()
AVX = False

SSSE3 = asm.cpu["ssse3"]
#SSSE3 = False
SSE3 = asm.cpu["sse3"]
SSE41 = asm.cpu["sse41"]
SSE2 = asm.cpu["sse2"]


def structs(*lst_structs):
    code = ""
    asm_structs = AsmStructures()

    for s in lst_structs:
        struct = asm_structs.get_struct(s)
        if struct is None:
           raise ValueError("Structure " + s + " doesn't exist!")
        code += struct

    return code
    

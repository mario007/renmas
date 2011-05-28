
from tdasm import Tdasm
import renmas.core
from renmas.core import AsmStructures


asm = Tdasm()
AVX = asm.avx_supported()
AVX = False

SSSE3 = asm.cpu["ssse3"]
#SSSE3 = False
SSE3 = asm.cpu["sse3"]
SSE41 = asm.cpu["sse41"]
#SSE41 = False
SSE2 = asm.cpu["sse2"]

def structs(*lst_structs):
    code = ""
    asm_structs = AsmStructures()

    for s in lst_structs:
        struct = asm_structs.get_struct(s)
        if struct is None:
           raise ValueError("Structure " + str(s) + " doesn't exist!")
        code += struct

    return code
    
assembler = None

def get_asm():

    from renmas.macros import eq32, eq128, eq32_32, eq32_128, eq128_128, eq128_32
    from renmas.macros import dot_product, macro_if, broadcast
    global assembler
    if assembler is None:
        assembler = Tdasm()
        assembler.register_macro("eq128", eq128)
        assembler.register_macro("eq32", eq32)

        assembler.register_macro("eq128_32", eq128_32)
        assembler.register_macro("eq32_128", eq32_128)
        assembler.register_macro("eq128_128", eq128_128)
        assembler.register_macro("eq32_32", eq32_32)

        assembler.register_macro("dot", dot_product)
        assembler.register_macro("if", macro_if)
        assembler.register_macro("broadcast", broadcast)

    return assembler

NUM = -1 
def unique():
    global NUM
    NUM += 1
    return NUM

# dynamic loadr of functions written in assembly 
# support functions have defined name
def load_func(runtime, *names):

    for name in names:
        if not runtime.global_exists(name):
            if name == "random":
                renmas.core.Rng.random_float(runtime, "random")
            pass # load that function


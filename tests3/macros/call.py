
from tdasm import Tdasm, Runtime
from renmas3.macros import MacroCall
import time

def asm_code(func_name):
    code = """
    #DATA
    float v1[4]
    float v2[4]
    #CODE
    movaps xmm0, oword [v1]
    movaps xmm1, oword [v2]
    """
    code += "macro call " + func_name + """
    movaps oword [v1], xmm0 
    movaps oword [v2], xmm6
    #END
    """
    return code

runtime = Runtime()
macro_call = MacroCall()
macro_call.set_runtimes([runtime])
assembler = Tdasm()
assembler.register_macro('call', macro_call.macro_call)

assembler.assemble(asm_code('fast_sin_ps'))
assembler.assemble(asm_code('fast_cos_ps'))

start = time.clock()
runtime = Runtime()
macro_call.set_runtimes([runtime])
end = time.clock()
print(end-start)


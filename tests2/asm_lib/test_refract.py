
import time
import math
from tdasm import Runtime
from renmas2.macros import MacroCall
from renmas2.utils import refract 
from renmas2.core import Factory

runtime = Runtime()
macro = MacroCall()
macro.set_runtimes([runtime])

factory = Factory()
v1 = factory.vector(-1, -1, 0)
v1.normalize()
n = factory.vector(0, 1, 0)
n.normalize()
n1 = 1.33
n2 = 1.0

t = refract(v1, n, n1, n2)
print(t)

asm_code = """
    #DATA
    float v[4]
    float n[4]
    float n1
    float n2
    float t[4]
    uint32 tir_ocured
    #CODE
    macro eq128 xmm0 = v
    macro eq128 xmm1 = n
    macro eq32 xmm2 = n1
    macro eq32 xmm3 = n2
    macro call refract 
    macro eq128 t = xmm0 {xmm7}
    mov dword [tir_ocured], eax
    #END
"""

asm = factory.create_assembler()
asm.register_macro('call', macro.macro_call)
mc = asm.assemble(asm_code)

ds = runtime.load('test', mc)
ds['v'] = v1.to_ds()
ds['n'] = n.to_ds()
ds['n1'] = n1
ds['n2'] = n2
runtime.run('test')
print(ds['t'])
print(ds['tir_ocured'])

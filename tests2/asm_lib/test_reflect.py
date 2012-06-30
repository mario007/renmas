import time
from tdasm import Runtime
from renmas2.macros import MacroCall
from renmas2.utils import reflect
from renmas2.core import Factory

runtime = Runtime()
macro = MacroCall()

start = time.clock()
macro.set_runtimes([runtime])
end = time.clock()
print(end-start)

factory = Factory()
v1 = factory.vector(-1, -1., -1)
n = factory.vector(0, 1, 0)

r = reflect(v1, n)
print(r)

asm_code = """
    #DATA
    float v[4]
    float n[4]
    float r[4]
    #CODE
    macro eq128 xmm0 = v
    macro eq128 xmm1 = n
    macro call reflect
    macro eq128 r = xmm0 {xmm7}
    #END
"""

asm = factory.create_assembler()
asm.register_macro('call', macro.macro_call)
mc = asm.assemble(asm_code)

ds = runtime.load('test', mc)
ds['v'] = v1.to_ds()
ds['n'] = n.to_ds()
runtime.run('test')
print(ds['r'])


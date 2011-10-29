
import renmas2
import time
import random
import math
from tdasm import Tdasm, Runtime
import renmas2.macros as mac


ASM = '''
#DATA
float v1[4]

#CODE
macro call random
movaps oword [v1], xmm0 

#END
'''

runtime = Runtime()
mac.macro_call.set_runtimes([runtime])
mc = mac.assembler.assemble(ASM)
ds = runtime.load('test_random', mc)

runtime.run('test_random')
print (ds['v1'])
runtime.run('test_random')
print (ds['v1'])




import renmas2
from tdasm import Runtime
import renmas2.macros as mac

ASM = '''
#DATA
float v1[4]

struct triangle
float p0[4]
end struct

triangle t1
float m1 = 5.5
float m2 = 2.3
float m3 = 2.1
float m4
float c = 1.0
float d = 2.0
float g = 1.0

float n1[4] = 2.2, 3.3, 4.4, 5.5
float n2[4] = 1.0, 1.0, 1.0, 1.0 
float nrez[4]

float brod[4]
float dot_rez

#CODE
macro eq32 xmm0 = m1 {xmm0}
macro eq32 xmm1 = m3 {xmm1}
macro eq32 xmm2 = m2 {xmm2}
macro eq32 m4 = xmm0 + xmm2 + xmm1 + c + d - g  {xmm5}

macro eq128 xmm4 = n1 - n2
macro eq128 nrez = xmm4 {xmm4}

macro broadcast xmm5 = xmm4[3]
macro eq128 brod = xmm5 {xmm0}

macro if xmm5 < d goto _lab

_lab:
macro dot xmm7 = n1 * n2 {xmm7, xmm6}
macro eq32 dot_rez = xmm7 {xmm7}

#END
'''

runtime = Runtime()
mac.macro_call.set_runtimes([runtime])
mc = mac.assembler.assemble(ASM)
#mc.print_machine_code()
ds = runtime.load('test_arithmetic', mc)

runtime.run('test_arithmetic')
print(ds['m4'])
print(ds['nrez'])
print(ds['brod'])
print(ds['dot_rez'])


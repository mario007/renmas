
from tdasm import Runtime
import renmas2


runtime = Runtime()
ren = renmas2.Renderer()
sk = renmas2.lights.SunSky(renderer=ren, latitude=80.0, longitude=43.0, sm=0, jd=224, time_of_day=16.50, turbidity=3.0)
ren.macro_call.set_runtimes([runtime])

ASM = """
    #DATA
    float theta, gamma, zenith, theta_sun
    float coeff[6]

    float temp 
    #CODE
    mov eax, coeff
    macro eq32 xmm0 = theta
    macro eq32 xmm1 = gamma 
    macro eq32 xmm2 = zenith 
    macro eq32 xmm3 = theta_sun 

    call perez_function
    macro eq32 temp = xmm0 {xmm7}
    #END
"""


sk._perez_function_asm("perez_function", [runtime], ren.assembler)

mc = ren.assembler.assemble(ASM)
ds = runtime.load("test", mc)

ret = sk._perez_function(sk._perez_x, 0.88, 0.56, sk._zenith_x)
print(ret)

ds['coeff'] = tuple(sk._perez_x) 
ds['theta_sun'] = sk._theta_sun
ds['zenith'] = sk._zenith_x
ds['theta'] = 0.88
ds['gamma'] = 0.56

runtime.run('test')
print(ds['temp'])



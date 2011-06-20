
import math
import renmas
import renmas.core
import renmas.samplers
import renmas.camera
import renmas.maths
import renmas.gui
import renmas.materials
import renmas.lights
import renmas.interface as ren 
import renmas.utils as util

from tdasm import Runtime

def map_to_hemisphere(x, y, e):

    cos_phi = math.cos(2.0 * math.pi * x)
    sin_phi = math.sin(2.0 * math.pi * x)
    cos_theta = math.pow((1.0 - y), 1.0 / (e + 1.0))
    sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)
    pu = sin_theta * cos_phi
    pv = sin_theta * sin_phi
    pw = cos_theta

hm = renmas.materials.HemisphereCos(1)

hitpoint = renmas.shapes.HitPoint()
hitpoint.hit_point = renmas.maths.Vector3(9.2, 40.5, 3.8)
hitpoint.normal = renmas.maths.Vector3(2.2, -4.3, 4.4)
hitpoint.normal.normalize()
hitpoint.wi = renmas.maths.Vector3(0.55, 0.35, 0.10)
hitpoint.wo = renmas.maths.Vector3(0.22, -0.66, 0.11)

spectrum = renmas.core.Spectrum(0.6, 0.7, 0.8)
ndotwi = 0.65

hitpoint.spectrum = spectrum
hitpoint.ndotwi = ndotwi

hm.get_sample(hitpoint)
hm.pdf(hitpoint)

asm_structs = renmas.utils.structs("hitpoint")
ASM = """
    #DATA
    """
ASM += asm_structs + """ 
    float _xmm0[4]
    float _xmm1[4]
    float _xmm2[4]
    float _xmm3[4]
    float _xmm4[4]
    float _xmm5[4]
    float _xmm6[4]
    float _xmm7[4]

    hitpoint hp1

    #CODE
    mov eax, hp1
    call get_sample

    macro eq128 _xmm0 = xmm0
    macro eq128 _xmm1 = xmm1
    macro eq128 _xmm2 = xmm2
    macro eq128 _xmm3 = xmm3
    macro eq128 _xmm4 = xmm4
    macro eq128 _xmm5 = xmm5
    macro eq128 _xmm6 = xmm6
    macro eq128 _xmm7 = xmm7
    #END
"""

asm = util.get_asm()
mc = asm.assemble(ASM)
runtime = Runtime()

hm.get_sample_asm(runtime, "get_sample")

ds = runtime.load("test", mc)
hpn = hitpoint.normal
ds["hp1.normal"] = (hpn.x, hpn.y, hpn.z, 0.0)

runtime.run("test")

print(ds["hp1.ndotwi"])
print(ds["hp1.wi"])

print(hitpoint.wi)
print(hitpoint.ndotwi)


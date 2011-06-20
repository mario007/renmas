
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


mat = renmas.materials.Material()
mat_spec = renmas.core.Spectrum(0.2, 0.2, 0.2)
lamb = renmas.materials.LambertianBRDF(mat_spec)

mat_spec2 = renmas.core.Spectrum(0.3, 0.2, 0.1)
lamb2 = renmas.materials.PhongBRDF(mat_spec2, 1.2)

#mat.add_component(lamb)
mat.add_component(lamb2)

runtime = Runtime()
mat.brdf_asm(runtime)

asm_structs = renmas.utils.structs("hitpoint")
ASM = """
    #DATA
"""
ASM += asm_structs + """
    hitpoint hp1
    uint32 func_ptr

    #CODE
    mov eax, hp1
    call dword [func_ptr]

    #END
"""
asm = util.get_asm()
mc = asm.assemble(ASM) 
ds = runtime.load("test", mc)

s = hitpoint.spectrum
ds["hp1.spectrum"] = (s.r, s.g, s.b, 0.0)
ds["hp1.ndotwi"] = hitpoint.ndotwi
wo = hitpoint.wo
ds["hp1.wo"] = (wo.x, wo.y, wo.z, 0.0)
wi = hitpoint.wi
ds["hp1.wi"] = (wi.x, wi.y, wi.z, 0.0)

norm = hitpoint.normal
ds["hp1.normal"] = (norm.x, norm.y, norm.z, 0.0)
ds["func_ptr"] = mat.func_ptr

runtime.run("test")

print(mat.brdf(hitpoint))
print(ds["hp1.spectrum"])


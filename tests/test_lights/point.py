
import renmas
import renmas.core
import renmas.samplers
import renmas.camera
import renmas.maths
import renmas.gui
import renmas.lights
import renmas.interface as ren 
import renmas.utils as util

from tdasm import Runtime

def build_scene():
    ren.create_sphere(0, 0, 0, 2)
    
    shapes = ren.lst_shapes()
    return shapes

def visible(runtime):
    dyn_arrays = ren.dyn_arrays()
    renmas.shapes.linear_isect_asm(runtime, "scene_isect", dyn_arrays)
    renmas.shapes.visible_asm(runtime, "visible", "scene_isect")

runtime = Runtime()
build_scene()
visible(runtime)

col = renmas.core.Spectrum(0.05, 0.05, 0.05) 
pos = renmas.maths.Vector3(10.0, 5.0, 8.0)
plight = renmas.lights.PointLight(pos, col) 

hitpoint = renmas.shapes.HitPoint()
hitpoint.hit_point = renmas.maths.Vector3(9.2, 40.5, 3.8)
hitpoint.normal = renmas.maths.Vector3(2.2, -4.3, 4.4)
hitpoint.normal.normalize()

asm_structs = renmas.utils.structs("hitpoint")
plight.L_asm(runtime, "visible")
ASM = """
    #DATA
"""
ASM += asm_structs + """
    hitpoint hp1
    uint32 func_ptr

    uint32 rez
    #CODE
    mov eax, hp1
    call dword [func_ptr]

    mov dword [rez], eax
    
    #END
"""

asm = util.get_asm()
mc = asm.assemble(ASM) 
ds = runtime.load("test", mc)

v = hitpoint.hit_point
ds["hp1.hit"] = (v.x, v.y, v.z, 0.0)
v = hitpoint.normal
ds["hp1.normal"] = (v.x, v.y, v.z, 0.0)
ds["func_ptr"] = plight.func_ptr


runtime.run("test")
print(ds["hp1.wi"])
print(ds["hp1.ndotwi"])
print(ds["hp1.spectrum"])
print(ds["hp1.visible"])

if plight.L(hitpoint):
    print("Python")
    print(hitpoint.visible)
    print(hitpoint.spectrum)
    print(hitpoint.wi)
    print(hitpoint.ndotwi)


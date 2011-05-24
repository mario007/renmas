
from tdasm import Runtime
import renmas
import renmas.shapes
import renmas.utils
import renmas.maths
import renmas.interface as ren 
import random

asm_structs = renmas.utils.structs("ray", "hitpoint")

def gen_random_shapes(n):
    for x in range(n):
        i = random.randint(0, 2)
        if i == 0:
            ren.random_sphere()
        elif i == 1:
            ren.random_plane()
        else:
            ren.random_triangle()

def ray_ds(ds, ray, name):
    o = ray.origin
    d = ray.dir
    ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
    ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    hitpoint hp
    uint32 hit 

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    call scene_isect 
    mov dword [hit], eax

    #END

"""
gen_random_shapes(10)
shapes = ren.lst_shapes()
dyn_arrays = ren.dyn_arrays()

runtime = Runtime()
renmas.shapes.linear_isect_asm(runtime, "scene_isect", dyn_arrays)

asm = renmas.utils.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("isect", mc)
ray = ren.random_ray()
ray_ds(ds, ray, "r1")

runtime.run("isect")


hp = renmas.shapes.isect(ray, shapes, 999999.0)

if hp is not None:
    print(hp.t, ds["hp.t"], ds["hit"])
else:
    print(ds["hit"])


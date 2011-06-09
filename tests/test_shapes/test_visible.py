
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


def gen_sphere():
    ren.create_sphere(0, 0, 0, 2)
    
ASM = """
#DATA
"""
ASM += asm_structs + """

    float p1[4] = 2.2, 1.3, 1.1, 0.0
    float p2[4] = 0.2, 3.8, 4.1, 0.0

    float origin[4]
    float direction[4]

    uint32 vis 
    #CODE
    movaps xmm0, oword [p1]
    movaps xmm1, oword [p2]
    call visible
    movaps oword [origin], xmm0
    movaps oword [direction], xmm1
    mov dword [vis], eax
    #END

"""
gen_random_shapes(10)
#gen_sphere()
shapes = ren.lst_shapes()
dyn_arrays = ren.dyn_arrays()

runtime = Runtime()
renmas.shapes.linear_isect_asm(runtime, "scene_isect", dyn_arrays)
renmas.shapes.visible_asm(runtime, "visible", "scene_isect")

asm = renmas.utils.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("visible", mc)

runtime.run("visible")

p1 = renmas.maths.Vector3(2.2, 1.3, 1.1)
p2 = renmas.maths.Vector3(0.2, 3.8, 4.1)

#p1 = renmas.maths.Vector3(10.0, 5.0, 8.0)
#p2 = renmas.maths.Vector3(9.2, 40.5, 3.8)

print(renmas.shapes.visible(p1, p2))

print(ds["vis"])
print(ds["origin"])
#print(ds["origin"])
#print(ds["direction"])


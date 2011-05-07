
from tdasm import Tdasm, Runtime
from renmas.macros import arth128, arth32, arth128_32, arth32_32
from renmas.macros import dot_product, macro_if

import random
from renmas.shapes import Plane
from renmas.core import Ray
from renmas.maths import Vector3
import renmas.utils as util

asm_structs = util.structs("ray", "plane", "hitpoint")

ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    plane p1
    hitpoint hp
    float min_dist = 1000.0
    float epsilon = 0.0001
    float t
    uint32 hit
    
#CODE
    mov eax, r1
    mov ebx, p1
    mov ecx, min_dist
    mov edx, hp

    call _plane_intersect
    movss dword [t], xmm4
    mov dword [hit], eax
#END
    ;eax = pointer to ray structure
    ;ebx = pointer to plane structure
    ;ecx = pointer to minimum distance
    ;edx = pointer to hitpoint

    _plane_intersect:
    macro arth128 xmm0 = ebx.plane.normal
    macro dot xmm1 = eax.ray.dir * xmm0 
    macro arth128 xmm2 = ebx.plane.point - eax.ray.origin {xmm0, xmm1}
    macro dot xmm3 = xmm2 * xmm0 {xmm1}
    macro arth32 xmm4 = xmm3 / xmm1

    macro if xmm4 > epsilon goto populate_hitpoint
    mov eax, 0 
    ret
    
    populate_hitpoint:
    mov eax, 1
    ret
"""

def generate_ray():
    x = random.random() * 10.0
    y = random.random() * 10.0
    z = random.random() * 10.0

    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    origin = Vector3(x, y, z)
    direction = Vector3(dir_x, dir_y, dir_z)
    direction.normalize()
    ray = Ray(origin, direction)
    return ray

def generate_plane():
    point = Vector3(0.0, 0.0, 1.0)
    normal = Vector3(0.0, 1.0, 0.0)
    plane = Plane(point, normal, None)
    return plane
    
def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

if __name__ == "__main__":
    asm = Tdasm()
    asm.register_macro("arth128", arth128)
    asm.register_macro("arth32", arth32)
    asm.register_macro("arth128_32", arth128_32)
    asm.register_macro("arth32_32", arth32_32)
    asm.register_macro("dot", dot_product)
    asm.register_macro("if", macro_if)
    mc = asm.assemble(ASM)
    #mc.print_machine_code()
    runtime = Runtime()
    ds = runtime.load("test", mc)

    for x in range(10):
        pl = generate_plane()
        ray = generate_ray()
        
        ds["r1.origin"] = v4(ray.origin)
        ds["r1.dir"] = v4(ray.dir)
        ds["p1.point"] = v4(pl.point)
        ds["p1.normal"] = v4(pl.normal)
        h = pl.intersect(ray)
        runtime.run("test")

        if h is False:
            print ("Py = ", h, "  ASM hit = " ,  ds["hit"])
        else:
            print("Py = ", h.t, "  ASM hit = " , ds["hit"], " ", ds["t"])


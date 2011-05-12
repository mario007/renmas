
from tdasm import Tdasm, Runtime
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
    float min_dist = 999999.0
    float epsilon = 0.0001
    float t
    uint32 hit
    
#CODE
    mov eax, r1
    mov ebx, p1
    mov ecx, min_dist

    call _plane_intersect
    mov dword [hit], eax

#END
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

def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

if __name__ == "__main__":
    asm = util.get_asm()
    mc = asm.assemble(ASM)
    #mc.print_machine_code()
    runtime = Runtime()
    Plane.intersectbool_asm(runtime, "_plane_intersect")
    ds = runtime.load("test", mc)

    for x in range(100000):
        #pl = generate_plane()
        pl = Plane.generate_plane()

        ray = generate_ray()
        
        ds["r1.origin"] = v4(ray.origin)
        ds["r1.dir"] = v4(ray.dir)
        ds["p1.point"] = v4(pl.point)
        ds["p1.normal"] = v4(pl.normal)
        ds["p1.mat_index"] = pl.material

        h = pl.intersect(ray)
        runtime.run("test")
        if h is False and ds["hit"] == 1:
            print (h, ds["hit"])
        if h is not False and ds["hit"] == 0:
            print (h, ds["hit"])


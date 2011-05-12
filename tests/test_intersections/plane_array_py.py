
from tdasm import Tdasm, Runtime
import random
from renmas.shapes import Plane
from renmas.core import Ray
from renmas.maths import Vector3
import renmas.utils as util
import timeit


asm_structs = util.structs("ray", "plane", "hitpoint")

ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    hitpoint hp
    float min_dist = 999999.0

    uint32 ptr_planes
    uint32 nplanes
    
    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, dword [ptr_planes]
    mov edi, dword [nplanes]
    ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_planes, edi - nplanes
    call plane_array 

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

def generate_planes(n):
    dyn_array = util.DynamicArray(Plane.struct())
    planes = []
    
    for x in range(n):
        plane = Plane.generate_plane()
        dyn_array.add_instance(plane.struct_params())
        planes.append(plane)
    return planes, dyn_array


def ray_objects(ray, objs):
    min_dist = 999999.0
    hit_point = None
    for s in objs:
        hit = s.intersect(ray, min_dist)
        if hit is False: continue
        if hit.t < min_dist:
            min_dist = hit.t
            hit_point = hit
    return hit_point

if __name__ == "__main__":
    asm = util.get_asm()
    mc = asm.assemble(ASM)
    #mc.print_machine_code()
    runtime = Runtime()
    Plane.intersect_asm(runtime, "_plane_intersect")
    Plane.intersect_array_asm(runtime, "plane_array", "_plane_intersect")
    ds = runtime.load("test", mc)
    
    planes, dyn_planes = generate_planes(10000)
    
    ray = generate_ray()
    hp = ray_objects(ray, planes)

    adr = dyn_planes.get_addr()
    ds["ptr_planes"] = adr
    ds["nplanes"] = dyn_planes.size
    
    ds["r1.origin"] = v4(ray.origin)
    ds["r1.dir"] = v4(ray.dir)

    t = timeit.Timer(lambda : runtime.run("test"))
    print ("time", t.timeit(1))

    #runtime.run("test")
    if hp is not False:
        print(hp.t, ds["hp.t"], ds["min_dist"])



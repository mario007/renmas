

import timeit
from tdasm import Tdasm, Runtime
import random
from renmas.shapes import Plane, Sphere, intersect_ray_shape_array, isect, linear_isect_asm, isect_ray_scene
from renmas.core import Ray, ShapeDatabase
from renmas.maths import Vector3
import renmas.utils as util

import renmas.interface as mdl

asm_structs = util.structs("ray", "plane", "sphere", "hitpoint")

def create_random_shapes(n, shape_db):

    for x in range(n):
        if random.random() > 0.5:
            shape = mdl.create_random_sphere()
            #shape = create_sphere()
        else:
            #shape = create_plane()
            shape = mdl.create_random_plane()
        shape_db.add_shape(shape)

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


ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    hitpoint hp
    float min_dist = 999999.0

    uint32 ptr_spheres
    uint32 nspheres

    uint32 ptr_planes
    uint32 nplanes
    
    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    call ray_scene
    #END

    ray_scene:
    mov eax, r1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, dword [ptr_spheres]
    mov edi, dword [nspheres]
    ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_spheres, edi - nspheres
    call sphere_array 

    mov eax, r1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, dword [ptr_planes]
    mov edi, dword [nplanes]
    call plane_array

"""

ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray r1
    hitpoint hp
    uint32 hit = 0

    
    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    call ray_scene
    mov dword [hit], eax
    #END

"""


def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

if __name__ == "__main__":

    shape_db = ShapeDatabase()
    #create_random_shapes(15, shape_db)
    t = timeit.Timer(lambda : create_random_shapes(6, shape_db))
    print ("time", t.timeit(1))

    t = timeit.Timer(lambda : shape_db.create_asm_arrays())
    print ("time", t.timeit(1))
    ray = generate_ray()

    t = timeit.Timer(lambda : isect(ray, shape_db.shapes()))
    print ("time", t.timeit(1))
    hp = isect(ray, shape_db.shapes())
    hp2 = isect_ray_scene(ray)

    asm = util.get_asm()

    dy_spheres = shape_db.asm_shapes[Sphere]
    dy_planes = shape_db.asm_shapes[Plane]

    #ds["r1.origin"] = v4(ray.origin)
    #ds["r1.dir"] = v4(ray.dir)
    
    runtime = Runtime()

    Sphere.intersect_asm(runtime, "_sphere_intersect")
    intersect_ray_shape_array("sphere", runtime, "sphere_array", "_sphere_intersect")
    Plane.intersect_asm(runtime, "_plane_intersect")
    intersect_ray_shape_array("plane", runtime, "plane_array", "_plane_intersect")

    mc = asm.assemble(ASM)

    ds = runtime.load("test", mc)

    ds["r1.origin"] = v4(ray.origin)
    ds["r1.dir"] = v4(ray.dir)
    ds["ptr_spheres"] = dy_spheres.get_addr()
    ds["nspheres"] = dy_spheres.size
    ds["ptr_planes"] = dy_planes.get_addr()
    ds["nplanes"] = dy_planes.size
    
    #runtime.run("test")
    t = timeit.Timer(lambda : runtime.run("test"))
    print ("time", t.timeit(1))

    runtime2 = Runtime()
    linear_isect_asm(runtime2, "ray_scene")
    mc2 = asm.assemble(ASM2)
    ds2 = runtime2.load("test3", mc2)
    ds2["r1.origin"] = v4(ray.origin)
    ds2["r1.dir"] = v4(ray.dir)
    runtime2.run("test3")

    print(ds2["hit"])
    if hp is not None:
        print(hp.t, ds["hp.t"], ds2["hp.t"], hp.material, ds["hp.mat_index"])
        print("hp2", hp2.t)
        print(hp.normal)
        print(ds["hp.normal"])
        


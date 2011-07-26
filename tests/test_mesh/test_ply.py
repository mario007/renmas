
import renmas
import renmas.interface as ren
import random
import renmas.utils as util
from tdasm import Runtime

def random_ray():
    x = random.random() * 10.0 - 5.0
    y = random.random() * 10.0 - 5.0
    z = random.random() * 10.0 - 5.0
    x = 0.0
    y = 0.0
    z = 0.0

    dir_x = 1.0 
    dir_y = 1.0 
    dir_z = 1.0 
    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    dir_x = -0.468824
    dir_y = 0.78302933
    dir_z = -0.40874

    origin = renmas.maths.Vector3(x, y, z)
    direction = renmas.maths.Vector3(dir_x, dir_y, dir_z)
    direction.normalize()
    ray = renmas.core.Ray(origin, direction)
    return ray

idx_material = 3
mesh = renmas.shapes.Mesh3D(idx_material)

#mesh.load_ply("TwoTriangles.ply")
#mesh.load_ply("Horse97K.ply")
mesh.load_ply("dragon_vrip_res4.ply")
#mesh.load_ply("dragon_vrip_res3.ply")
#mesh.load_ply("dragon_vrip_res2.ply")
#mesh.load_ply("dragon_vrip.ply")
#mesh.load_ply("happy_vrip.ply")

mesh.prepare_isect()

lst_triangles = mesh.lst_triangles()

print(len(lst_triangles))

isect = renmas.shapes.isect #intersection rutine
#for x in range(100):
#    ray = random_ray()
#    hp = isect(ray, lst_triangles, 999999.0)
#    if hp is not None: 
#        print(ray)
#        break


runtime = Runtime()
mesh.prepare_isect_asm(runtime)
print(mesh.attributes())

renmas.shapes.Mesh3D.isect_asm(runtime, "mesh_isect")



asm_structs = util.structs("ray", "mesh3d", "hitpoint")
ASM = """
    #DATA
"""
ASM +=  asm_structs + """
    ray ray1
    hitpoint hp
    float min_dist = 9999.99
    ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj

    mesh3d mesh1
    uint32 result

    #CODE
    mov eax, ray1
    mov ebx, mesh1 
    mov ecx, min_dist
    mov edx, hp
    call mesh_isect
    mov dword[result], eax

    #END
"""

def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

asm = util.get_asm()
mc = asm.assemble(ASM)
#mc.print_machine_code()
ds = runtime.load("test", mc)

ray = random_ray()
ds["ray1.origin"] = v4(ray.origin)
ds["ray1.dir"] = v4(ray.dir)
ds["mesh1.ptr_isect"] = mesh.ptr_isect

runtime.run("test")
runtime.run("test")
print("Nemoguce ", ds["hp.t"], ds["result"])

import timeit
t = timeit.Timer(lambda : isect(ray, lst_triangles, 999999.0))
print ("time", t.timeit(1))
t = timeit.Timer(lambda : mesh.isect(ray))
print ("time", t.timeit(1))
t = timeit.Timer(lambda : runtime.run("test"))
print ("time", t.timeit(1))

hp = isect(ray, lst_triangles, 999999.0)

hp2 = mesh.isect(ray)

if hp is not None:
    print (hp.t, hp2.t)


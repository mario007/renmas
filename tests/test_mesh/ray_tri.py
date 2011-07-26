
import renmas
import renmas.interface as ren
import renmas.utils as util
import random
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

    dir_x = -0.296138 
    dir_y =  0.900627
    dir_z =  0.318077

    dir_x = -0.468824
    dir_y = 0.78302933
    dir_z = -0.40874

    origin = renmas.maths.Vector3(x, y, z)
    direction = renmas.maths.Vector3(dir_x, dir_y, dir_z)
    direction.normalize()
    ray = renmas.core.Ray(origin, direction)
    return ray

idx_material = 2
mesh = renmas.shapes.Mesh3D(idx_material)

#mesh.load_ply("dragon_vrip_res4.ply")
mesh.load_ply("dragon_vrip_res3.ply")

mesh.prepare_isect()

runtime = Runtime()

mesh._ray_tri_asm(runtime, "ray_tri_isect")

asm_structs = util.structs("ray", "triangle", "hitpoint")
ASM = """
    #DATA
"""
ASM +=  asm_structs + """
    ray ray1
    hitpoint hp
    float min_dist = 9999.99
    ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj

    uint32 n = 10360 
    ;uint32 n = 10225 
    uint32 arr[12000] = 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12 
    uint32 ptr_array

    #CODE
    mov eax, ray1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, arr
    mov edi, dword [n]
    call ray_tri_isect


    #END
"""


def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

asm = util.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("test", mc)

ray = random_ray()
ds["ray1.origin"] = v4(ray.origin)
ds["ray1.dir"] = v4(ray.dir)

#lst = [n for n in range(10221)]
lst = [n for n in range(11300)]

lst = [7448, 7598, 7599, 7600, 7603, 7923, 7924, 7927, 8279, 8280, 8282, 8283, 8532, 8796, 9132, 9352, 9689, 9690]
lst = [8280]

ds["arr"] = tuple(lst)
ds["n"] = len(lst)

runtime.run("test")
print("asm hp.t = ", ds["hp.t"])

hp = mesh.isect_triangles(ray, lst)
print(ray.dir)
print(hp)
if hp:
    print(hp.t)




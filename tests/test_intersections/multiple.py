
import timeit
from tdasm import Tdasm, Runtime
import random
import renmas.shapes

import renmas.interface as ren 
from scenes import cornell_scene

def isect(ray, shapes, min_dist=999999.0):
    hit_point = None
    for s in shapes:
        hit = s.isect(ray, min_dist)
        if hit is False: continue
        if hit.t < min_dist:
            min_dist = hit.t
            hit_point = hit
    return hit_point

def test1():
    m_props = {"name": "m1", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 55.92), "edge_a":(55.28, 0.0, 0.0), "edge_b":(0.0, 54.88, 0.0), "normal":(0.0, 0.0, -1.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"rectangle", "p":(55.28, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(0.0, 54.88, 0.0), "normal":(-1.0, 0.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)

cornell_scene()

sh_props = {"type":"sphere", "position":(0,0,0), "radius":9, "material":"m1"}
s = ren.create_shape(sh_props)
sh_props = {"type":"triangle", "p0":(0.556,0.0,0.0), "p1":(0.006, 0.0, 0.559), "p2":(0.556, 0.0, 0.959) ,"material":"m1"}
s = ren.create_shape(sh_props)
sh_props = {"type":"triangle", "p0":(0.406,0.0,0.559), "p1":(0.556, 0.0, 0.0), "p2":(0.003, 0.0, 0.1) ,"material":"m1"}
s = ren.create_shape(sh_props)
## BACK WALL
sh_props = {"type":"triangle", "p0":(0.556,0.0,0.559), "p1":(0.0, 0.599, 0.559), "p2":(0.556, 0.549, 0.359) ,"material":"m2"}
s = ren.create_shape(sh_props)
sh_props = {"type":"triangle", "p0":(0.2,0.549,0.559), "p1":(0.756, 0.0, 0.559), "p2":(0.006, 0.0, 0.259) ,"material":"m2"}
s = ren.create_shape(sh_props)

runtime = Runtime()
lst_shapes = ren.lst_shapes()
adrese = ren.objfunc_array(lst_shapes, runtime)

asm_structs = renmas.utils.structs("sample", "ray", "hitpoint")
ASM = """
    #DATA
"""

ASM += asm_structs + """

    uint32 num
    uint32 addrs[256]
    hitpoint hp
    ray ray1
    float min_dist = 999999.3

    uint32 count = 100 
    uint32 clocks 

    #CODE
    
    rdtsc 
    mov dword [clocks], eax

    _petlja:
    
    mov eax, ray1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, addrs
    mov edi, dword [num]
    ;call _array_isect
    call multiple_isect

    sub dword [count], 1
    jnz _petlja

    rdtsc
    sub eax, dword [clocks]
    mov dword [clocks], eax

    #END


    ; eax - ray,  ebx - hp, ecx - min_dist, esi - ptr_arr, edi - nobj
    ; 64-bit version will bi i little different beacuse of different size of array
    _array_isect:
    push ecx
    push eax
    push ebx
    push esi
    push edi

    _objects_loop:
    mov eax, dword [esp + 12] ; address of ray
    mov ecx, dword [esp + 16] ; address of minimum distance
    mov edx, dword [esp + 8]  ; address of hitpoint
    mov esi, dword [esp + 4] ; array of objects and functions obj_ptr:func_ptr
    mov ebx, dword [esi]  ; put in ebx address of object
    call dword [esi + 4]  ; function pointer
    cmp eax, 0  ; 0 - no intersection ocur 1 - intersection ocur
    jne _update_distance
    _next_object:
    sub dword [esp], 1  
    jz _end_objects
    add dword [esp + 4], 8  ;increment array by 8
    jmp _objects_loop


    _update_distance:
    mov eax, dword [esp + 8]
    mov ebx, dword [eax + hitpoint.t]

    mov edx, dword [esp + 16] ;populate new minimum distance
    mov dword [edx], ebx
    jmp _next_object
    
    _end_objects:
    add esp, 20 
    ret


"""

asm = Tdasm()
renmas.shapes.multiple_isect_asm(runtime, "multiple_isect")
mc = asm.assemble(ASM)

def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

ds = runtime.load("test", mc)

ray = ren.random_ray()
ds["ray1.origin"] = v4(ray.origin)
ds["ray1.dir"] = v4(ray.dir)
ds["num"] = len(lst_shapes)
ds["addrs"] = adrese

runtime.run("test")

print(ds["hp.t"], ds["clocks"])

hp = isect(ray, lst_shapes)
print(hp.t)


runtime2 = Runtime()
renmas.shapes.linear_isect_asm(runtime2, "ray_scene", ren.dyn_arrays())


ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray ray1
    hitpoint hp
    uint32 hit = 0

    uint32 clocks 
    uint32 count = 100

    #CODE
    rdtsc 
    mov dword [clocks], eax

    _petlja:


    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, ray1
    mov ebx, hp
    call ray_scene

    sub dword [count], 1
    jnz _petlja

    rdtsc
    sub eax, dword [clocks]
    mov dword [clocks], eax

    #END

"""
mc2 = asm.assemble(ASM2)

ds2 = runtime2.load("test2", mc2)
ds2["ray1.origin"] = v4(ray.origin)
ds2["ray1.dir"] = v4(ray.dir)

runtime2.run("test2")

print(ds2["hp.t"], ds2["clocks"])


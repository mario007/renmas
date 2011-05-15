
from tdasm import Tdasm, Runtime
import random
from renmas.shapes import Sphere, intersect_ray_shape_array
from renmas.core import Ray
from renmas.maths import Vector3
import renmas.utils as util


if util.AVX:
    line1 = " vsqrtss xmm5, xmm5, xmm5 \n"
else:
    line1 = " sqrtss xmm5, xmm5 \n"

asm_structs = util.structs("ray", "sphere", "hitpoint")
ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    sphere sph
    hitpoint hp
    float min_dist = 999999.0
    float epsilon = 0.0001
    float t
    uint32 hit
    float two = 2.0
    float minus_four = -4.0
    float zero = 0.0
    float one = 1.0
    float minus_one = -1.0


    float a, b, disc
    float temp[4]


#CODE
    mov eax, r1
    mov ebx, sph 
    mov ecx, min_dist
    mov edx, hp

    call _sphere_intersect
    mov dword [hit], eax
    movss dword [t], xmm6
#END

    _sphere_intersect:
    macro eq128_128 xmm1 = eax.ray.dir, xmm2 = eax.ray.origin - ebx.sphere.origin
    macro dot xmm3 = xmm1 * xmm1 {xmm2}
    macro dot xmm4 = xmm2 * xmm1 {xmm3}
    macro eq32_32 xmm4 = xmm4 * two, xmm5 = ebx.sphere.radius * ebx.sphere.radius {xmm1, xmm2, xmm3, xmm4}
    macro dot xmm6 = xmm2 * xmm2 {xmm1, xmm3, xmm4, xmm5}
    macro eq32 xmm5 = xmm6 - xmm5 {xmm1, xmm2, xmm3, xmm4}
    macro eq32_32 xmm5 = xmm5 * xmm3, xmm6 = xmm4 * xmm4 {xmm1, xmm2, xmm3}
    macro eq32 xmm5 = xmm5 * minus_four {xmm1, xmm2, xmm3, xmm4, xmm6}
    macro eq32 xmm5 = xmm5 + xmm6 {xmm1, xmm2, xmm3, xmm4}
    
    ; temp = xmm2, a = xmm3 , b = xmm4, disc = xmm5, ray.dir = xmm1
    macro if xmm5 < zero goto _reject
"""
ASM += line1 + """
    macro eq32 xmm3 = xmm3 * two {xmm1, xmm2, xmm4, xmm5}
    macro eq32_32 xmm3 = one / xmm3, xmm4 = xmm4 * minus_one {xmm1, xmm2, xmm5}
    macro eq32 xmm6 = xmm4 - xmm5 {xmm1, xmm2, xmm3, xmm5}
    macro eq32 xmm6 = xmm6 * xmm3 {xmm1, xmm2, xmm3, xmm4, xmm5}
    macro if xmm6 > epsilon goto populate_hitpoint
    macro eq32 xmm6 = xmm4 + xmm5 {xmm1, xmm2, xmm3}
    macro eq32 xmm6 = xmm6 * xmm3 {xmm1, xmm2, xmm3, xmm4, xmm5}
    macro if xmm6 > epsilon goto populate_hitpoint
    mov eax, 0
    ret

    populate_hitpoint:
    macro if xmm6 > ecx goto _reject 
    macro broadcast xmm5 = xmm6[0]
    macro eq128_32 xmm4 =  xmm5 * xmm1, xmm7 = ebx.sphere.radius {xmm2}
    macro eq32 edx.hitpoint.t = xmm6 {xmm2, xmm4, xmm7}
    macro eq128_128 edx.hitpoint.hit = xmm4 + eax.ray.origin, xmm5 = xmm2 + xmm4 {xmm7}
    macro broadcast xmm7 = xmm7[0] 
    macro eq128_32 edx.hitpoint.normal = xmm5 / xmm7, edx.hitpoint.mat_index = ebx.sphere.mat_index

    mov eax, 1
    ret

    _reject:
    mov eax, 0
    ret

"""

ASM1 = """
#DATA
"""
ASM1 += asm_structs + """

    ray r1
    sphere sph
    hitpoint hp
    float min_dist = 999999.0
    float epsilon = 0.0001
    float t
    uint32 hit
    float two = 2.0
    float minus_four = -4.0
    float zero = 0.0
    float one = 1.0
    float minus_one = -1.0


    float a, b, disc
    float temp[4]


#CODE
    mov eax, r1
    mov ebx, sph 
    mov ecx, min_dist
    mov edx, hp

    call ray_sphere_intersect 
    mov dword [hit], eax
    movss dword [t], xmm6
#END

"""

ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray r1
    hitpoint hp
    float min_dist = 999999.0

    uint32 ptr_spheres
    uint32 nspheres
    
    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    mov ecx, min_dist
    mov esi, dword [ptr_spheres]
    mov edi, dword [nspheres]
    ; eax - ray, ebx - hp , ecx - min_dist, esi - ptr_spheres, edi - nspheres
    call sphere_array 

    #END

"""
def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

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

def generate_sphere():
    x = random.random() * 10.0 - 5.0
    y = random.random() * 10.0 - 5.0
    z = random.random() * 10.0 - 5.0
    radius = random.random() * 10.0 

    sphere = Sphere(Vector3(x, y, z), radius, 2)
    return sphere

def generate_spheres(n):
    dyn_array = util.DynamicArray(Sphere.struct())
    spheres = []
    
    for x in range(n):
        sphere = generate_sphere() 
        dyn_array.add_instance(sphere.struct_params())
        spheres.append(sphere)
    return spheres, dyn_array

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

def intersect_ray_spheres(n, runtime, ds):
    for x in range(n):
        sphere = generate_sphere()
        ray = generate_ray()
        ds["sph.origin"] = v4(sphere.origin)
        ds["sph.radius"] = sphere.radius
        ds["sph.mat_index"] = sphere.material

        ds["r1.origin"] = v4(ray.origin)
        ds["r1.dir"] = v4(ray.dir)

        hp = sphere.intersect(ray, 999999.0)
        
        runtime.run("test")
        
        if hp is not False and ds["hit"] == 0:
            print(hp.t, ds["t"], ds["hit"])
        if hp is False and ds["hit"] == 1:
            print(ds["t"], ds["hit"])

        #if hp is not False:
        #    print(hp.t, ds["t"], ds["hit"])
        #    #print(ds["a"], ds["b"], ds["disc"], ds["temp"])
        #else:
        #    print (hp, ds["hit"])
    
def intersect_sphere(runtime, ds):
    sphere = Sphere(Vector3(0.0, 0.0, 0.0), 1.5, 2)
    direction = Vector3(-7.0, -7.0, -6.0)
    direction.normalize()
    ray = Ray(Vector3(8.0, 7.0, 6.0), direction)
    ds["sph.origin"] = v4(sphere.origin)
    ds["sph.radius"] = sphere.radius
    ds["sph.mat_index"] = sphere.material

    ds["r1.origin"] = v4(ray.origin)
    ds["r1.dir"] = v4(ray.dir)

    hp = sphere.intersect(ray, 999999.0)
    
    runtime.run("test")
    if hp is not False:
        print(hp.t, ds["t"], ds["hit"])
        print("Python =", hp.t, "Asm = ", ds["hp.t"])
        print("Python =", hp.hit_point)
        print("Asm =", ds["hp.hit"])
        print("Python =", hp.normal)
        print("Asm =", ds["hp.normal"])
        print("Python = ", hp.material, " ASM = ", ds["hp.mat_index"])

        #print(ds["a"], ds["b"], ds["disc"], ds["temp"])
    else:
        print (hp, ds["hit"])

def print_hitpoint(ds, hp):
    print(hp.t, ds["t"], ds["hit"])
    print("Python =", hp.t, "Asm = ", ds["hp.t"])
    print("Python =", hp.hit_point)
    print("Asm =", ds["hp.hit"])
    print("Python =", hp.normal)
    print("Asm =", ds["hp.normal"])
    print("Python = ", hp.material, " ASM = ", ds["hp.mat_index"])

def intersect_ray_spheres_bool(n):
    asm = util.get_asm()
    mc = asm.assemble(ASM1)
    runtime = Runtime()
    
    #Sphere.intersectbool_asm(runtime, "ray_sphere_intersect")
    Sphere.intersect_asm(runtime, "ray_sphere_intersect")
    ds = runtime.load("test", mc)

    for x in range(n):
        sphere = generate_sphere()
        ray = generate_ray()
        ds["sph.origin"] = v4(sphere.origin)
        ds["sph.radius"] = sphere.radius
        ds["sph.mat_index"] = sphere.material

        ds["r1.origin"] = v4(ray.origin)
        ds["r1.dir"] = v4(ray.dir)

        hp = sphere.intersect(ray, 999999.0)
        
        runtime.run("test")
        
        if hp is not False and ds["hit"] == 0:
            print(hp.t, ds["t"], ds["hit"])
        if hp is False and ds["hit"] == 1:
            print(ds["t"], ds["hit"])

        if hp is not False:
            print_hitpoint(ds, hp)

if __name__ == "__main__":

    asm = util.get_asm()
    mc = asm.assemble(ASM)
    #mc.print_machine_code()

    runtime = Runtime()
    #ds = runtime.load("test", mc)

    #intersect_sphere(runtime, ds) 
    #intersect_ray_spheres(100000, runtime, ds) 
    #intersect_ray_spheres_bool(10)

    Sphere.intersect_asm(runtime, "_sphere_intersect")
    intersect_ray_shape_array("sphere", runtime, "sphere_array", "_sphere_intersect")
    mc = asm.assemble(ASM2)
    ds = runtime.load("test2", mc)
    spheres, dyn_spheres = generate_spheres(1000)

    ray = generate_ray()
    hp = ray_objects(ray, spheres)

    adr = dyn_spheres.get_addr()
    ds["ptr_spheres"] = adr
    ds["nspheres"] = dyn_spheres.size
    
    ds["r1.origin"] = v4(ray.origin)
    ds["r1.dir"] = v4(ray.dir)

    runtime.run("test2")

    if hp is not None:
        print(hp.t, ds["hp.t"], ds["min_dist"])

    


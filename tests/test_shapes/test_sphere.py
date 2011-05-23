
from tdasm import Runtime
import renmas
import renmas.shapes
import renmas.utils
import renmas.maths
import renmas.interface as ren 
import random

def random_spheres(n):
    for x in range(n):
        ren.random_sphere()

asm_structs = renmas.utils.structs("ray", "sphere", "hitpoint")

ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    sphere sph
    hitpoint hp
    float min_dist = 999999.0
    uint32 hit 

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_sphere
    mov eax, r1
    mov ebx, sph 
    mov ecx, min_dist
    mov edx, hp
    call sphere_isect 
    mov dword [hit], eax

    #END

"""
def random_sphere():
    x = random.random() * 10.0 - 5.0
    y = random.random() * 10.0 - 5.0
    z = random.random() * 10.0 - 5.0
    radius = random.random() * 1.50 
    
    v1 = renmas.maths.Vector3(x, y, z)
    sphere = renmas.shapes.Sphere(v1, radius, 99999)
    return sphere

def isect_ray_sphere(populate=True):
    mc = renmas.utils.get_asm().assemble(ASM)
    runtime = Runtime()
    renmas.shapes.Sphere.isect_asm(runtime, "sphere_isect", populate)
    ds = runtime.load("isect", mc)
    return (runtime, ds)

def ray_ds(ds, ray, name):
    o = ray.origin
    d = ray.dir
    ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
    ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

def sphere_ds(ds, sphere, name):
    o = sphere.origin
    ds[name+".origin"] = (o.x, o.y, o.z, 0.0) 
    ds[name+".radius"] = sphere.radius
    ds[name+".mat_index"] = sphere.material

def isect_bool(runtime, ds, n):
    nhits = 0
    for x in range(n):
        sph = random_sphere()
        ray = ren.random_ray()
        
        ray_ds(ds, ray, "r1")
        sphere_ds(ds, sph, "sph")

        runtime.run("isect")
        hit =  ds["hit"]
        hp = sph.isect(ray, 999999.0)

        if hp is not False:
            nhits += 1
            if ds["hit"] == 0:
                raise ValueError("Intersection of ray - sphere problem")
        if ds["hit"] == 1:
            if hp is False:
                raise ValueError("Intersection of ray - sphere problem")
    print("Number of hits", nhits, ds["hp.t"])

def isect_sphere(runtime, ds, n):
    nhits = 0
    for x in range(n):
        sph = random_sphere()
        ray = ren.random_ray()
        
        ray_ds(ds, ray, "r1")
        sphere_ds(ds, sph, "sph")

        runtime.run("isect")
        hit =  ds["hit"]
        hp = sph.isect(ray, 999999.0)

        if hp is not False:
            if round(hp.t, 1) != round(ds["hp.t"], 1):
                print(hp.t, ds["hp.t"])
                raise ValueError("Intersection of ray - sphere rounding")

            nhits += 1
            if ds["hit"] == 0:
                raise ValueError("Intersection of ray - sphere problem")
        if ds["hit"] == 1:
            if hp is False:
                raise ValueError("Intersection of ray - sphere problem")
    print("Number of hits", nhits)        

def test_bool():
    runtime, ds = isect_ray_sphere(False)
    isect_bool(runtime, ds, 100000)

def test_isect():
    runtime, ds = isect_ray_sphere()
    isect_sphere(runtime, ds, 100000)


ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray r1
    sphere sph
    hitpoint hp
    float min_dist = 999999.0
    uint32 hit 

    uint32 ptr_spheres
    uint32 nspheres

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp 
    mov ecx, min_dist
    mov esi, dword [ptr_spheres] 
    mov edi, dword [nspheres]
    call sphere_array
    mov dword [hit], eax

    #END

"""

def isect_ray_sphere_array():
    mc = renmas.utils.get_asm().assemble(ASM2)
    runtime = Runtime()
    renmas.shapes.Sphere.isect_asm(runtime, "sphere_isect")
    renmas.shapes.intersect_ray_shape_array("sphere", runtime, "sphere_array", "sphere_isect")
    ds = runtime.load("isect", mc)
    return (runtime, ds)

def test_linear():
    runtime, ds = isect_ray_sphere_array()
    random_spheres(1000)
    shapes = ren.lst_shapes()
    ray = ren.random_ray()
    ray_ds(ds, ray, "r1")

    dyn_arrays = ren.dyn_arrays()
    ds["nspheres"] = dyn_arrays[renmas.shapes.Sphere].size
    ds["ptr_spheres"] = dyn_arrays[renmas.shapes.Sphere].get_addr()

    runtime.run("isect")
    hp = renmas.shapes.isect(ray, shapes, 999999.0)
    if hp is not None:
        print(hp.t, ds["hp.t"])


test_bool()
test_isect()
test_linear()



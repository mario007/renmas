
from tdasm import Runtime
import renmas
import renmas.shapes
import renmas.utils
import renmas.maths
import renmas.interface as ren 
import random

def random_planes(n):
    for x in range(n):
        ren.random_plane()

asm_structs = renmas.utils.structs("ray", "plane", "hitpoint")

ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    plane pl 
    hitpoint hp
    float min_dist = 999999.0
    uint32 hit 

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_sphere
    mov eax, r1
    mov ebx, pl 
    mov ecx, min_dist
    mov edx, hp
    call plane_isect 
    mov dword [hit], eax

    #END

"""

def random_plane():
    x = random.random() * 10.0
    y = random.random() * 10.0
    z = random.random() * 10.0

    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    point = renmas.maths.Vector3(x, y, z)
    normal = renmas.maths.Vector3(dir_x, dir_y, dir_z)
    normal.normalize()

    plane = renmas.shapes.Plane(point, normal, 99999)
    return plane

def isect_ray_plane(populate=True):
    mc = renmas.utils.get_asm().assemble(ASM)
    runtime = Runtime()
    renmas.shapes.Plane.isect_asm(runtime, "plane_isect", populate)
    ds = runtime.load("isect", mc)
    return (runtime, ds)

def ray_ds(ds, ray, name):
    o = ray.origin
    d = ray.dir
    ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
    ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

def plane_ds(ds, plane, name):
    n = plane.normal 
    p = plane.point
    ds[name+".normal"] = (n.x, n.y, n.z, 0.0) 
    ds[name+".point"] = (p.x, p.y, p.z, 0.0)
    ds[name+".mat_index"] = plane.material

def isect_bool(runtime, ds, n):
    nhits = 0
    for x in range(n):
        pl = random_plane()
        ray = ren.random_ray()
        
        ray_ds(ds, ray, "r1")
        plane_ds(ds, pl, "pl")

        runtime.run("isect")
        hit =  ds["hit"]
        hp = pl.isect(ray, 999999.0)

        if hp is not False:
            nhits += 1
            if ds["hit"] == 0:
                raise ValueError("Intersection of ray - sphere problem")
        if ds["hit"] == 1:
            if hp is False:
                raise ValueError("Intersection of ray - sphere problem")
    print("Number of hits", nhits, ds["hp.t"])

def isect_plane(runtime, ds, n):
    nhits = 0
    for x in range(n):
        pl = random_plane()
        ray = ren.random_ray()
        
        ray_ds(ds, ray, "r1")
        plane_ds(ds, pl, "pl")

        runtime.run("isect")
        hit =  ds["hit"]
        hp = pl.isect(ray, 999999.0)

        if hp is not False:
            if round(hp.t, 0) != round(ds["hp.t"], 0):
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
    runtime, ds = isect_ray_plane(False)
    isect_bool(runtime, ds, 100000)

def test_isect():
    runtime, ds = isect_ray_plane()
    isect_plane(runtime, ds, 100000)

ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray r1
    plane pl 
    hitpoint hp
    float min_dist = 999999.0
    uint32 hit 

    uint32 ptr_planes
    uint32 nplanes

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp 
    mov ecx, min_dist
    mov esi, dword [ptr_planes] 
    mov edi, dword [nplanes]
    call plane_array
    mov dword [hit], eax

    #END

"""

def isect_ray_plane_array():
    mc = renmas.utils.get_asm().assemble(ASM2)
    runtime = Runtime()
    renmas.shapes.Plane.isect_asm(runtime, "plane_isect")
    renmas.shapes.intersect_ray_shape_array("plane", runtime, "plane_array", "plane_isect")
    ds = runtime.load("isect", mc)
    return (runtime, ds)

def test_linear():
    runtime, ds = isect_ray_plane_array()
    random_planes(1000)
    shapes = ren.lst_shapes()
    ray = ren.random_ray()
    ray_ds(ds, ray, "r1")

    dyn_arrays = ren.dyn_arrays()
    ds["nplanes"] = dyn_arrays[renmas.shapes.Plane].size
    ds["ptr_planes"] = dyn_arrays[renmas.shapes.Plane].get_addr()

    runtime.run("isect")
    hp = renmas.shapes.isect(ray, shapes, 999999.0)
    if hp is not None:
        print(hp.t, ds["hp.t"])

#test_bool()
#test_isect()
test_linear()


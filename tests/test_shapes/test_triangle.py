
from tdasm import Runtime
import renmas
import renmas.shapes
import renmas.utils
import renmas.maths
import renmas.interface as ren 
import random

def random_triangles(n):
    for x in range(n):
        ren.random_triangle()

asm_structs = renmas.utils.structs("ray", "triangle", "hitpoint")

ASM = """
#DATA
"""
ASM += asm_structs + """

    ray r1
    triangle tri
    hitpoint hp
    float min_dist = 999999.0
    uint32 hit 

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_triangle
    mov eax, r1
    mov ebx, tri 
    mov ecx, min_dist
    mov edx, hp
    call triangle_isect 
    mov dword [hit], eax

    #END

"""

def random_triangle():
    p0 = renmas.maths.Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
    p1 = renmas.maths.Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
    p2 = renmas.maths.Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
    tri = renmas.shapes.Triangle(p0, p1, p2, 99999)
    return tri

def isect_ray_triangle(populate=True):
    mc = renmas.utils.get_asm().assemble(ASM)
    runtime = Runtime()
    renmas.shapes.Triangle.isect_asm(runtime, "triangle_isect", populate)
    ds = runtime.load("isect", mc)
    return (runtime, ds)

def ray_ds(ds, ray, name):
    o = ray.origin
    d = ray.dir
    ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
    ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)

def triangle_ds(ds, triangle, name):
    p0 = triangle.v0 
    p1 = triangle.v1
    p2 = triangle.v2
    n = triangle.normal

    ds[name+".p0"] = (p0.x, p0.y, p0.z, 0.0) 
    ds[name+".p1"] = (p1.x, p1.y, p1.z, 0.0) 
    ds[name+".p2"] = (p2.x, p2.y, p2.z, 0.0) 
    ds[name+".normal"] = (n.x, n.y, n.z, 0.0) 
    ds[name+".mat_index"] = triangle.material

def isect_bool(runtime, ds, n):
    nhits = 0
    for x in range(n):
        tri = random_triangle()
        ray = ren.random_ray()
        
        ray_ds(ds, ray, "r1")
        triangle_ds(ds, tri, "tri")

        runtime.run("isect")
        hit =  ds["hit"]
        hp = tri.isect(ray, 999999.0)

        if hp is not False:
            nhits += 1
            if ds["hit"] == 0:
                raise ValueError("Intersection of ray - sphere problem")
        if ds["hit"] == 1:
            if hp is False:
                raise ValueError("Intersection of ray - sphere problem")
    print("Number of hits", nhits, ds["hp.t"])

def isect_triangle(runtime, ds, n):
    nhits = 0
    for x in range(n):
        tri = random_triangle()
        ray = ren.random_ray()
        
        ray_ds(ds, ray, "r1")
        triangle_ds(ds, tri, "tri")

        runtime.run("isect")
        hit =  ds["hit"]
        hp = tri.isect(ray, 999999.0)

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
    runtime, ds = isect_ray_triangle(False)
    isect_bool(runtime, ds, 100000)

def test_isect():
    runtime, ds = isect_ray_triangle()
    isect_triangle(runtime, ds, 100000)

ASM2 = """
#DATA
"""
ASM2 += asm_structs + """

    ray r1
    triangle tri 
    hitpoint hp
    float min_dist = 999999.0
    uint32 hit 

    uint32 ptr_triangles
    uint32 ntriangle

    #CODE
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp 
    mov ecx, min_dist
    mov esi, dword [ptr_triangles] 
    mov edi, dword [ntriangle]
    call triangle_array
    mov dword [hit], eax

    #END

"""

def isect_ray_triangle_array():
    mc = renmas.utils.get_asm().assemble(ASM2)
    runtime = Runtime()
    renmas.shapes.Triangle.isect_asm(runtime, "triangle_isect")
    renmas.shapes.intersect_ray_shape_array("triangle", runtime, "triangle_array", "triangle_isect")
    ds = runtime.load("isect", mc)
    return (runtime, ds)

def test_linear():
    runtime, ds = isect_ray_triangle_array()
    random_triangles(1000)
    shapes = ren.lst_shapes()
    ray = ren.random_ray()
    ray_ds(ds, ray, "r1")

    dyn_arrays = ren.dyn_arrays()
    ds["ntriangle"] = dyn_arrays[renmas.shapes.Triangle].size
    ds["ptr_triangles"] = dyn_arrays[renmas.shapes.Triangle].get_addr()

    runtime.run("isect")
    hp = renmas.shapes.isect(ray, shapes, 999999.0)
    if hp is not None:
        print(hp.t, ds["hp.t"])

test_bool()
test_isect()
test_linear()


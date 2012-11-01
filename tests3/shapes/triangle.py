
from tdasm import Runtime

from renmas3.base import Vector3, Ray
from renmas3.shapes import Triangle, HitPoint
from renmas3.macros import create_assembler

v0 = Vector3(2.2, 4.4, 6.6)
v1 = Vector3(1.1, 1.1, 1.1)
v2 = Vector3(5.1, -1.1, 5.1)

n0 = Vector3(1.1, -1.6, 1.1)
n1 = Vector3(1.1, -2.1, 3.1)
n2 = Vector3(4.1, -0.1, 2.1)

origin = Vector3(0.0, 0.0, 0.0)
direction = Vector3(3, 3.0, 3.01)
direction.normalize()
ray = Ray(origin, direction)
t = Triangle(v0, v1, v2, n0=n0, n1=n1, n2=n2, tu0=0.1, tv0=0.6, tu1=0.2,
        tv1=0.5, tu2=0.45, tv2=0.2)

hit = t.isect(ray)

runtime1 = Runtime()
runtimes = [runtime1]

asm = create_assembler()
Triangle.isect_asm(runtimes, "ray_triangle_intersection", asm)

code = """
    #DATA
"""
code += Ray.asm_struct() + Triangle.asm_struct() + HitPoint.asm_struct() + """
    ray ray1
    triangle tri1
    hitpoint hp1
    uint32 ret

    #CODE
    macro mov eax, ray1
    macro mov ebx, tri1
    macro mov edx, hp1
    call ray_triangle_intersection 
    mov dword [ret], eax
    #END
"""
mc = asm.assemble(code)
ds = runtime1.load("test", mc)

def ray_ds(ds, ray, name):
    ds[name+ ".origin"] = ray.origin.to_ds() 
    ds[name+ ".dir"] = ray.dir.to_ds()

def triangle_ds(ds, triangle, name):
    ds[name+ ".v0"] = triangle.v0.to_ds() 
    ds[name+ ".v1"] = triangle.v1.to_ds()
    ds[name+ ".v2"] = triangle.v2.to_ds()
    if triangle.has_normals:
        ds[name+ ".n0"] = triangle.n0.to_ds()
        ds[name+ ".n1"] = triangle.n1.to_ds()
        ds[name+ ".n2"] = triangle.n2.to_ds()
        ds[name+ ".has_normals"] = 1
    else:
        ds[name+ ".normal"] = triangle.normal.to_ds()
        ds[name+ ".has_normals"] = 0

    if triangle.has_uv:
        ds[name+ ".has_uv"] = 1
        ds[name+ ".tu0"] = triangle.tu0
        ds[name+ ".tu1"] = triangle.tu1
        ds[name+ ".tu2"] = triangle.tu2
        ds[name+ ".tv0"] = triangle.tv0
        ds[name+ ".tv1"] = triangle.tv1
        ds[name+ ".tv2"] = triangle.tv2
    else:
        ds[name+ ".has_uv"] = 0


ray_ds(ds, ray, 'ray1')
triangle_ds(ds, t, "tri1")

runtime1.run("test")

if hit:
    print('hit=true ', 'ds["ret"]=', ds['ret'])
    print(hit.t, ds['hp1.t'])
    print(hit.hit)
    print(ds['hp1.hit'])
    print('----------------------------')
    print(hit.normal)
    print(ds['hp1.normal'])
    print('----------------------------')
    print(hit.material_idx, ds['hp1.material_idx'])
    print('----------------------------')
    print(hit.u, hit.v)
    print(ds['hp1.u'], ds['hp1.v'])



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

min_dist = 1.93
hit = t.isect(ray, min_dist)

runtime1 = Runtime()
runtimes = [runtime1]

asm = create_assembler()
Triangle.isect_asm(runtimes, "ray_triangle_intersection")

code = """
    #DATA
"""
code += Ray.asm_struct() + Triangle.asm_struct() + HitPoint.asm_struct() + """
    Ray ray1
    Triangle tri1
    Hitpoint hp1
    uint32 ret
    float min_dist = 1.92
    float _xmm0

    #CODE
    macro mov eax, ray1
    macro mov ebx, tri1
    macro mov ecx, min_dist
    macro mov edx, hp1
    call ray_triangle_intersection 
    mov dword [ret], eax
    macro eq32 _xmm0 = xmm0 {xmm0}
    #END
"""
mc = asm.assemble(code)
ds = runtime1.load("test", mc)

Ray.populate_ds(ds, ray, 'ray1')
Triangle.populate_ds(ds, t, 'tri1')
ds['min_dist'] = min_dist

runtime1.run("test")

if hit:
    print('hit=true ', 'ds["ret"]=', ds['ret'])
    print(hit.t, ds['hp1.t'], ds['_xmm0'])
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
else:
    print('hit=flase', 'ds["ret"]=', ds['ret'])


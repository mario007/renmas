
from tdasm import Tdasm, Runtime
import renmas2.core
import renmas2.shapes

ASM_CODE = """
    #DATA
"""
ASM_CODE += renmas2.core.get_structs(('ray', 'sphere', 'hitpoint')) + """
    ray ray1
    sphere sph1
    hitpoint hp1
    float min_dist = 99999.000
    float a, b, c, disc, e, t
    #CODE
    mov eax, ray1
    mov ebx, sph1
    mov ecx, min_dist
    mov edx, hp1
    call ray_sphere_intersection 
    movss dword [a], xmm0
    movss dword [b], xmm3
    movss dword [c], xmm2
    movss dword [disc], xmm4
    movss dword [e], xmm5
    movss dword [t], xmm7
    #END
"""

def get_ray():
    origin = renmas2.core.Vector3(5.0, 5.0, 5.0)
    direction = renmas2.core.Vector3(-1.0, -1.0, -1.0)
    direction.normalize()
    ray = renmas2.core.Ray(origin, direction)
    return ray

def get_sphere():
    center = renmas2.core.Vector3(0.0, 0.0, 0.0)
    radius = 2.0
    sph = renmas2.shapes.Sphere(center, radius, 0)
    return sph

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

    
ray = get_ray()
sph = get_sphere()

runtime = Runtime()
sph.isect_asm([runtime], 'ray_sphere_intersection')
asm = Tdasm()
mc = asm.assemble(ASM_CODE)
ds = runtime.load('test', mc)

ray_ds(ds, ray, 'ray1')
sphere_ds(ds, sph, 'sph1')

runtime.run('test')

hp = sph.isect(ray)

if hp:
    print(hp.t, ds['hp1.t'])
    print(hp.hit_point)
    print(ds['hp1.hit'])
    print(hp.normal)
    print(ds['hp1.normal'])
    print(hp.material, ds['hp1.mat_index'])



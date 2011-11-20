import random
import time
from tdasm import Tdasm, Runtime
import renmas2
import renmas2.shapes

inter = renmas2.core.Intersector()

ASM_CODE = """
    #DATA
"""
    # eax - ray
    # ebx - hitpoint
    # ecx - min_dist
    # esi - ptr_array
    # edi - nshapes 
ASM_CODE += renmas2.core.get_structs(('ray', 'sphere', 'hitpoint')) + """
    ray ray1
    hitpoint hp1
    float min_dist = 99999.000
    uint32 ptr_array
    uint32 nshapes

    #CODE
    mov eax, ray1
    mov ebx, hp1
    ;mov ecx, min_dist
    ;mov esi, dword [ptr_array]
    ;mov edi, dword [nshapes] 
    ;call ray_spheres_intersection 
    call ray_scene_intersection
    #END
"""

def random_spheres(intersecotr, n):
    for i in range(n):
        center = renmas2.core.Vector3(0.0, 0.0, 0.0)
        radius = random.random() * 1.5 
        sph = renmas2.shapes.Sphere(center, radius, 0)
        inter.add('sphere'+str(i), sph)

def get_ray():
    origin = renmas2.core.Vector3(5.0, 5.0, 5.0)
    direction = renmas2.core.Vector3(-1.0, -1.0, -1.0)
    direction.normalize()
    ray = renmas2.core.Ray(origin, direction)
    return ray

def ray_ds(ds, ray, name):
    o = ray.origin
    d = ray.dir
    ds[name+ ".origin"] = (o.x, o.y, o.z, 0.0)
    ds[name+ ".dir"] = (d.x, d.y, d.z, 0.0)


start = time.clock()
random_spheres(inter, 200)
end = time.clock()
print(end-start)

runtime = Runtime()
renmas2.shapes.Sphere.isect_asm([runtime], 'ray_sphere_intersection')
#inter._isect_ray_shape_array_asm('sphere', [runtime], 'ray_spheres_intersection', 'ray_sphere_intersection')
inter._isect_ray_scene([runtime], 'ray_scene_intersection', inter._shape_arrays)

ray = get_ray()
inter.prepare()

asm = Tdasm()
mc = asm.assemble(ASM_CODE)
ds = runtime.load('test', mc)
ray_ds(ds, ray, 'ray1')
ds['ptr_array'] = inter._shape_arrays[renmas2.shapes.Sphere].get_addr() 
ds['nshapes'] = inter._shape_arrays[renmas2.shapes.Sphere].size 

runtime.run('test')

hp = inter.isect(ray)
if hp:
    print(hp.t, ds['hp1.t'])
    print(hp.hit_point)
    print(ds['hp1.hit'])
    print(hp.normal)
    print(ds['hp1.normal'])
    print(hp.material, ds['hp1.mat_index'])
else:
    print('No intersection ocur')



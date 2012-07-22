
from random import random

from tdasm import Runtime
from renmas3.core import Renderer, ShapeManager, Factory
from renmas3.core.structures import SHADEPOINT, RAY

factory = Factory()
def random_sphere():
    origin = (random(), random(), random())
    return factory.sphere(origin, random())

def random_ray():
    origin = (random(), random(), random())
    direction = (random(), random(), random())
    return factory.ray(origin, direction)

def ray_ds(ds, ray, name):
    ds[name+ ".origin"] = ray.origin.to_ds() 
    ds[name+ ".dir"] = ray.dir.to_ds() 

ren = Renderer()
mgr = ShapeManager(ren)
mgr.add('sphere1', random_sphere())
mgr.add('sphere2', random_sphere())
mgr.add('sphere3', random_sphere())
mgr.prepare()

runtime = Runtime()
mgr.isect_asm([runtime], 'ray_scene_intersection')

def asm_code(ren):
    # eax - ray
    # ebx - hitpoint
    code = "#DATA \n" + ren.color_mgr.spectrum_struct() + RAY + SHADEPOINT + """
        ray ray1
        shadepoint hp1
        uint32 ret

        #CODE
        macro mov eax, ray1
        macro mov ebx, hp1
        call ray_scene_intersection
        mov dword [ret], eax
        #END
    """
    return code

mc = ren.assembler.assemble(asm_code(ren))
ds = runtime.load('test', mc)

def generate_tests(n, ds):
    for i in range(n):
        ray = random_ray()
        ray_ds(ds, ray, 'ray1')

        sp = mgr.isect(ray)
        runtime.run('test')
        if sp:
            print(sp.t, ds['hp1.t'], ds['ret'])
        else:
            print(sp, ds['ret'])

generate_tests(10, ds)
mgr.visibility_asm([runtime], 'visible')

def asm_vis():
    code = """
        #DATA 
        uint32 ret
        float p0[4]
        float p1[4]

        #CODE
        macro eq128 xmm0 = p0
        macro eq128 xmm1 = p1
        call visible 
        mov dword [ret], eax
        #END
    """
    return code

mc = ren.assembler.assemble(asm_vis())
ds2 = runtime.load('visible', mc)

print('*********************************')
def test_visibility(n, ds):
    for i in range(n):
        p1 = factory.vector3(random(), random(), random())
        p2 = factory.vector3(random(), random(), random())
        ds['p0'] = p1.to_ds()
        ds['p1'] = p2.to_ds()
        
        vis = mgr.visibility(p1, p2)
        runtime.run('visible')
        vis2 = ds['ret']
        print(vis, vis2)

test_visibility(10, ds2)


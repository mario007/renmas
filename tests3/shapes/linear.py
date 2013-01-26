
from tdasm import Tdasm, Runtime
from renmas3.base import Vector3, Ray
from renmas3.shapes import LinearIsect, ShapeManager, Triangle, HitPoint
from renmas3.macros import create_assembler
from renmas3.base import BasicShader, Integer

v0 = Vector3(2.2, 4.4, 6.6)
v1 = Vector3(1.1, 1.1, 1.1)
v2 = Vector3(5.1, -1.1, 5.1)

t = Triangle(v0, v1, v2)

v0 = Vector3(2.6, 4.4, 6.6)
v1 = Vector3(1.2, 1.1, 1.1)
v2 = Vector3(5.1, -1.1, 5.1)

t2 = Triangle(v0, v1, v2)

mgr = ShapeManager()
mgr.add('t1', t)
mgr.add('t2', t2)

origin = Vector3(0.2, 0.4, 0.6)
direction = Vector3(1.2, 1.1, 1.12)
direction.normalize()
ray = Ray(origin, direction)

linear = LinearIsect(mgr)

hit = linear.isect(ray)

runtime = Runtime()
linear.isect_asm([runtime], 'ray_scene_intersection')

code = "#DATA \n"
code += Ray.asm_struct() + HitPoint.asm_struct() + """
    Ray ray1
    Hitpoint hp1
    uint32 ret

    #CODE
    macro mov eax, ray1
    macro mov ebx, hp1
    call ray_scene_intersection 
    mov dword [ret], eax
    #END
"""
asm = create_assembler()
mc = asm.assemble(code)

ds = runtime.load('test', mc)

def ray_ds(ds, ray, name):
    ds[name+ ".origin"] = ray.origin.to_ds() 
    ds[name+ ".dir"] = ray.dir.to_ds()

ray_ds(ds, ray, 'ray1')
runtime.run('test')
print (hit, hit.t)
print (hit.normal)
print (ds['ret'], ds['hp1.t'])
print (ds['hp1.normal'])
print ('------------------')


shader = linear.isect_shader([runtime])
hit2 = HitPoint()
props = {'hit': hit2, 'ret': 0, 'ray': ray}
code = """
ret = isect(ray, hit)
"""
bs = BasicShader(code, None, props)
bs.prepare([runtime], [shader])

bs.execute()
print (bs.shader.get_value('ret'))
print (bs.shader.get_value('hit.t'))
print (bs.shader.get_value('hit.normal'))


linear.visibility_asm([runtime], 'visibility')
code = """
    #DATA
    uint32 ret
    float p1[4] = 0.2, 0.2, 0.2, 0.0
    float p2[4] = 1.5, 1.5, 1.5, 0.0
    float _xmm0[4]

    #CODE
    macro eq128 xmm0 = p1
    macro eq128 xmm1 = p2
    call visibility 
    mov dword [ret], eax
    macro eq128 _xmm0 = xmm0 {xmm7}
    #END
"""
p1 = Vector3(0.2, 0.2, 0.2)
p2 = Vector3(1.5, 1.5, 1.51)
mc = asm.assemble(code)
ds = runtime.load('test_vis', mc)
ds['p1'] = p1.to_ds()
ds['p2'] = p2.to_ds()
runtime.run('test_vis')
print("--------------")
print("Points are visible", ds['ret'])
print(linear.visibility(p1, p2))
print(ds['_xmm0'])


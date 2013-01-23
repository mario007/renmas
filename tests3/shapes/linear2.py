import time
from random import random
from tdasm import Tdasm, Runtime
from renmas3.base import Vector3, Ray
from renmas3.shapes import LinearIsect, ShapeManager, Triangle
from renmas3.shapes import HitPoint, load_meshes
from renmas3.macros import create_assembler
from renmas3.base import VertexBuffer, VertexNBuffer, VertexUVBuffer, VertexNUVBuffer, TriangleBuffer


def create_triangle(v0, v1, v2, n0=None, n1=None, n2=None,
                     uv0=None, uv1=None, uv2=None):

    p0 = Vector3(v0[0], v0[1], v0[2])
    p1 = Vector3(v1[0], v1[1], v1[2])
    p2 = Vector3(v2[0], v2[1], v2[2])
    if n0 is not None:
        n0 = Vector3(n0[0], n0[1], n0[2])
        n1 = Vector3(n1[0], n1[1], n1[2])
        n2 = Vector3(n2[0], n2[1], n2[2])
    if uv0 is not None:
        tu0, tv0 = uv0
        tu1, tv1 = uv1
        tu2, tv2 = uv2
    else:
        tu0 = tv0 = tu1 = tv1 = tu2 = tv2 = None

    t = Triangle(p0, p1, p2, n0=n0, n1=n1, n2=n2, tu0=tu0,
            tv0=tv0, tu1=tu1, tv1=tv1, tu2=tu2, tv2=tv2)
    return t

def populate(mgr, tb, vb):
    counter = 0
    name = "t" + str(id(tb))
    for i in range(tb.size()):
        idx1, idx2, idx3 = tb.get(i)
        if isinstance(vb, VertexBuffer):
            v0 = vb.get(idx1)
            v1 = vb.get(idx2)
            v2 = vb.get(idx3)
            n0 = n1 = n2 = uv0 = uv1 = uv2 = None
        elif isinstance(vb, VertexNBuffer):
            v0, n0 = vb.get(idx1)
            v1, n1 = vb.get(idx2)
            v2, n2 = vb.get(idx3)
            uv0 = uv1 = uv2 = None
        elif isinstance(vb, VertexUVBuffer):
            v0, uv0 = vb.get(idx1)
            v1, uv1 = vb.get(idx2)
            v2, uv2 = vb.get(idx3)
            n0 = n1 = n2 = None
        elif isinstance(vb, VertexNUVBuffer):
            v0, n0, uv0 = vb.get(idx1)
            v1, n1, uv1 = vb.get(idx2)
            v2, n2, uv2 = vb.get(idx3)
        else:
            raise ValueError("Unknown vertex buffer", vb)

        t = create_triangle(v0, v1, v2, n0=n0, n1=n1, n2=n2,
                             uv0=uv0, uv1=uv1, uv2=uv2)
        mgr.add(name+str(counter), t)
        counter += 1

def populate_mgr(mgr, fname):
    meshes = load_meshes(fname)
    for m in meshes:
        populate(mgr, m.tb, m.vb)

#fname = "F://ray_tracing_scenes/cube/cube.obj"
fname = "F://ray_tracing_scenes/dragon/dragon.obj"
#fname = "F://ray_tracing_scenes/head/head.obj"
mgr = ShapeManager()
populate_mgr(mgr, fname)

linear = LinearIsect(mgr)
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

origin = Vector3(0.2, 0.4, 0.6)
direction = Vector3(1.2, 1.1, 1.12)
direction.normalize()
ray = Ray(origin, direction)


def ray_ds(ds, ray, name):
    ds[name+ ".origin"] = ray.origin.to_ds() 
    ds[name+ ".dir"] = ray.dir.to_ds()

def random_ray(ds):
    origin = Vector3(0.0, 0.0, 0.0)
    direction = Vector3(random(), random(), random())
    direction.normalize()
    ray = Ray(origin, direction)
    ray_ds(ds, ray, 'ray1')
    return ray

for i in range(5):
    ray = random_ray(ds)
    start = time.clock()
    hit = linear.isect(ray)
    end = time.clock()
    dur1 = end-start
    start = time.clock()
    runtime.run('test')
    end = time.clock()
    dur2 = end-start
    if hit:
        print(hit.t, ds['hp1.t'], ds['ret'], dur1, dur2)
    else:
        print("False ", ds['ret'], dur1, dur2)



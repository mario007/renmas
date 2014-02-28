
import time
import random
from tdasm import Runtime
from sdl import Vector3, StructArg, Shader, Ray, IntArg
from renlgt.mesh import load_meshes, create_mesh, FlatMesh
from renlgt.hitpoint import HitPoint


def random_in_bbox(bbox):
    x = random.uniform(bbox.x0, bbox.x1)
    y = random.uniform(bbox.y0, bbox.y1)
    z = random.uniform(bbox.z0, bbox.z1)
    return Vector3(x, y, z)


def calculate_origin(mesh):
    bbox = mesh._grid.bbox

    wx = bbox.x1 - bbox.x0
    wy = bbox.y1 - bbox.y0
    wz = bbox.z1 - bbox.z0
    cx = (bbox.x1 + bbox.x0) / 2.0
    cy = (bbox.y1 + bbox.y0) / 2.0
    cz = (bbox.z1 + bbox.z0) / 2.0

    ox = cx - wx
    oy = cy - wy
    oz = cz - wz
    return Vector3(ox, oy, oz)


def test_mesh(mesh, nrays=1):
    dep_shader = type(mesh).isect_shader('ray_flat_mesh_isect')
    dep_shader.compile()
    runtimes = [Runtime()]
    dep_shader.prepare(runtimes)

    code = """
min_dist = 99999.0
ret = ray_flat_mesh_isect(ray, mesh, hitpoint, min_dist)
    """

    origin = calculate_origin(mesh)
    rpoint = random_in_bbox(mesh._grid.bbox)
    direction = rpoint - origin 
    direction.normalize()

    ray = Ray(origin, direction)
    hitpoint = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                            Vector3(0.0, 0.0, 0.0), 6, 0.0, 0.0)

    r_arg = StructArg('ray', ray)
    mesh_arg = StructArg('mesh', mesh)
    harg = StructArg('hitpoint', hitpoint)
    ret = IntArg('ret', 6)

    args = [r_arg, mesh_arg, harg, ret]
    shader = Shader(code=code, args=args)
    shader.compile([dep_shader.shader])

    shader.prepare(runtimes)

    hp = mesh.isect(ray)
    shader.execute()

    print(hp, shader.get_value('ret'))
    if hp:
        hp_new = shader.get_value('hitpoint')
        print(hp.t, hp_new.t)
        # print(hp.u, hp_new.u, hp.v, hp_new.v)
        # print(hp.hit)
        # print(hp_new.hit)
        # print('Norma')
        # print(hp.normal)
        # print(hp_new.normal)


def test_mesh_b(mesh, nrays=1):
    dep_shader = type(mesh).isect_b_shader('ray_flat_mesh_b_isect')
    dep_shader.compile()
    runtimes = [Runtime()]
    dep_shader.prepare(runtimes)

    code = """
min_dist = 99999.0
ret = ray_flat_mesh_b_isect(ray, mesh, min_dist)
    """

    origin = calculate_origin(mesh)
    rpoint = random_in_bbox(mesh._grid.bbox)
    direction = rpoint - origin 
    direction.normalize()

    ray = Ray(origin, direction)
    r_arg = StructArg('ray', ray)
    mesh_arg = StructArg('mesh', mesh)
    ret = IntArg('ret', 6)

    args = [r_arg, mesh_arg, ret]
    shader = Shader(code=code, args=args)
    shader.compile([dep_shader.shader])

    shader.prepare(runtimes)

    hp = mesh.isect_b(ray)
    shader.execute()
    print("Bool isect", hp, shader.get_value('ret'))


start = time.clock()
#fdesc = load_meshes('E:\Ply_files\cube.ply')
#fdesc = load_meshes('E:\Ply_files\dragon_vrip.ply')
#fdesc = load_meshes('E:\Ply_files\dragon_vrip_res4.ply')
#fdesc = load_meshes('E:\Ply_files\lucy.ply')
#fdesc = load_meshes('E:\Ply_files\power_plant\ppsection1\part_a\g0.ply')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\teapot\teapot.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\conference\conference.obj')
fdesc = load_meshes(r'E:\ray_tracing_scenes\cube\cube.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\buddha\buddha.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\san-miguel\san-miguel.obj')
elapsed = time.clock() - start
# print("Time to load mesh file took %f seconds" % elapsed)
# print(fdesc.fname)
for mdesc in fdesc.mesh_descs:
    mesh = create_mesh(mdesc, mat_idx=0)
    start = time.clock()
    mesh.prepare()
    elapsed = time.clock() - start
    # print("Preparing mesh took %f seconds" % elapsed)

    test_mesh(mesh, nrays=1)
    test_mesh_b(mesh, nrays=1)


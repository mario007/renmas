
import time
import random
from tdasm import Runtime
from sdl import Vector3, StructArg, Shader, Ray, IntArg
from renlgt.mesh import load_meshes, create_mesh, FlatMesh
from renlgt.hitpoint import HitPoint


def isect_ray_triangle(ray, p0, p1, p2, min_dist=99999.0): #ray direction must be normalized

    a = p0[0] - p1[0]
    b = p0[0] - p2[0]
    c = ray.direction.x 
    d = p0[0] - ray.origin.x
    e = p0[1] - p1[1]
    f = p0[1] - p2[1]
    g = ray.direction.y
    h = p0[1] - ray.origin.y
    i = p0[2] - p1[2]
    j = p0[2] - p2[2]
    k = ray.direction.z
    l = p0[2] - ray.origin.z

    m = f * k - g * j
    n = h * k - g * l
    p = f * l - h * j
    q = g * i - e * k
    s = e * j - f * i

    temp3 =  (a * m + b * q + c * s)

    if temp3 == 0.0:
        return False
    inv_denom = 1.0 / temp3

    e1 = d * m - b * n - c * p
    beta = e1 * inv_denom

    if beta < 0.0:
        return False

    r = e * l - h * i
    e2 = a * n + d * q + c * r
    gamma = e2 * inv_denom

    if gamma < 0.0:
        return False

    if beta + gamma > 1.0:
        return False

    e3 = a * p - b * r + d * s
    t = e3 * inv_denom

    if t < 0.00001:
        return False # self-intersection

    if t > min_dist:
        return False

    hit_point = ray.origin + ray.direction * t

    normal = Vector3(0.0, 0.0, 0.0)

    return HitPoint(t, hit_point, normal, 0, 0.0, 0.0)


def isect_ray_mesh(ray, mesh):

    min_dist = 99999.0
    hit_point = None
    index = -1

    for idx in range(mesh.ntriangles()):
        p0, p1, p2 = mesh.get_points(idx)
        hp = isect_ray_triangle(ray, p0, p1, p2, min_dist)
        if hp and hp.t < min_dist:
            hit_point = hp
            min_dist = hp.t
            index = idx
    return hit_point, index


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


def generate_ray(mesh):
    origin = calculate_origin(mesh)
    rpoint = random_in_bbox(mesh._grid.bbox)
    direction = rpoint - origin 
    direction.normalize()

    ray = Ray(origin, direction)
    return ray


def test_mesh(mesh, nrays=1):
    dep_shader = type(mesh).isect_shader('ray_flat_mesh_isect')
    dep_shader.compile()
    runtimes = [Runtime()]
    dep_shader.prepare(runtimes)

    code = """
min_dist = 99999.0
ret = ray_flat_mesh_isect(ray, mesh, hitpoint, min_dist)
    """

    ray = generate_ray(mesh)
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

    for i in range(nrays):
        ray = generate_ray(mesh)
        # origin = Vector3(-0.21099534597992897,-0.02090535280108452,-0.09716709856688976)
        # direction = Vector3(0.7856996643888073,0.4629769683728137,0.4102783983292736)
        # ray = Ray(origin, direction)
        shader.set_value('ray', ray)

        hp2 = mesh.isect(ray)
        hp, index = isect_ray_mesh(ray, mesh)
        shader.execute()

        # print(hp, shader.get_value('ret'))
        if hp:
            ret = shader.get_value('ret')
            hp_new = shader.get_value('hitpoint')
            if round(hp.t - hp_new.t, 5) != 0:
                print(hp.t, hp_new.t, ret, index, hp2.t)
                print(ray.origin)
                print(ray.direction)
                p0, p1, p2 = mesh.get_points(index)
                print(p0)
                print(p1)
                print(p2)
                print('------------------------------------------')
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
fdesc = load_meshes('E:\Ply_files\dragon_vrip_res4.ply')
#fdesc = load_meshes('E:\Ply_files\lucy.ply')
#fdesc = load_meshes('E:\Ply_files\power_plant\ppsection1\part_a\g0.ply')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\teapot\teapot.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\conference\conference.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\cube\cube.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\buddha\buddha.obj')
#fdesc = load_meshes(r'E:\ray_tracing_scenes\san-miguel\san-miguel.obj')
elapsed = time.clock() - start
# print("Time to load mesh file took %f seconds" % elapsed)
# print(fdesc.fname)
for mdesc in fdesc.mesh_descs:
    mesh = create_mesh(mdesc.vb, mdesc.tb, mat_idx=0)
    start = time.clock()
    mesh.prepare()
    elapsed = time.clock() - start
    # print("Preparing mesh took %f seconds" % elapsed)

    test_mesh(mesh, nrays=10)
    test_mesh_b(mesh, nrays=1)


import time
from tdasm import Runtime
from renmas3.base import Ray, Vector3
from renmas3.macros import create_assembler
from renmas3.shapes import ShapeManager, LinearIsect
from renmas3.shapes import FlatMesh, random_in_bbox, Triangle, HitPoint
from renmas3.shapes import fetch_triangle, load_meshes_from_file

def asm_code(label_ray_mesh_isect, mesh):
    struct_name = mesh.asm_struct_name()
    code = """
        #DATA
    """
    code += Ray.asm_struct() + mesh.asm_struct() + HitPoint.asm_struct() + """
        Ray ray1
    """
    code += struct_name + " mesh1" + """
        Hitpoint hp1
        float min_dist = 99999.000
        float max_dist = 99999.000
        uint32 ret
        float t
        #CODE
        macro eq32 min_dist = max_dist {xmm7}
        macro mov eax, ray1
        macro mov ebx, mesh1
        macro mov ecx, min_dist
        macro mov edx, hp1
    """
    code += "call " + label_ray_mesh_isect + """ 
        mov dword [ret], eax
        macro eq32 t = xmm0 {xmm7}
        #END
    """
    return code

def generate_ray(bbox):
    dir = random_in_bbox(bbox) 
    dir.normalize()
    origin = Vector3(0.0, 0.0, 0.0)
    return Ray(origin, dir)

def populate_mgr_with_triangles(mgr, mesh):
    for i in range(mesh.ntriangles()):
        tri = fetch_triangle(mesh, i)
        name = "Tri %i" % i
        mgr.add(name, tri)

def compare_floats(val1, val2, places=3):
    if round(val1, places) != round(val2, places):
        raise ValueError("Floats are different ", val1, val2)

def compare_tuple(val1, val2, places=3):
    for v1, v2 in zip(val1, val2):
        if round(v1, places) != round(v2, places):
            raise ValueError("Floats are different ", v1, v2)

def test_mesh_isect(mesh, nrays=1):
    mgr = ShapeManager()
    print("Populate shape manager with %i triangles" % mesh.ntriangles())
    start = time.clock()
    populate_mgr_with_triangles(mgr, mesh)
    print("Population of shape manager took %f seconds" % (time.clock() - start,))

    runtimes = [Runtime()]
    mesh.isect_asm(runtimes, "ray_mesh_isect")
    assembler = create_assembler()
    mc = assembler.assemble(asm_code("ray_mesh_isect", mesh))
    runtime = runtimes[0]
    ds = runtime.load("test", mc)
    mesh.populate_ds(ds, mesh, "mesh1")

    isector = LinearIsect(mgr)
    bbox = mesh.bbox()
    print("Intersection tests begin")
    for i in range(nrays):
        ray = generate_ray(bbox)
        ray.populate_ds(ds, ray, "ray1")

        hp1 = mesh.isect(ray)
        hp2 = isector.isect(ray)
        runtime.run("test")
        if hp1 is False and hp2 is False and ds['ret'] == 0:
            continue
        if hp1 is False and hp2 is not False:
            print(ray)
            raise ValueError("Intersection error!")
        if hp1 is False and ds['ret'] == 1:
            print(ray)
            raise ValueError("Intersection error!")
        compare_floats(hp1.t, hp2.t)
        compare_floats(hp1.t, ds["hp1.t"])
        normal1 = (hp1.normal.x, hp1.normal.y, hp1.normal.z)
        normal2 = (hp2.normal.x, hp2.normal.y, hp2.normal.z)
        normal3 = ds["hp1.normal"][0:3]
        compare_tuple(normal1, normal2)
        compare_tuple(normal1, normal3)

        hit1 = (hp1.hit.x, hp1.hit.y, hp1.hit.z)
        hit2 = (hp2.hit.x, hp2.hit.y, hp2.hit.z)
        hit3 = ds["hp1.hit"][0:3]
        compare_tuple(hit1, hit2)
        compare_tuple(hit1, hit3)

        if mesh.has_uv():
            compare_floats(hp1.u, hp2.u)
            compare_floats(hp1.v, hp2.v)
            compare_floats(hp1.u, ds["hp1.u"]) 
            compare_floats(hp1.v, ds["hp1.v"]) 


def test_mesh_isect_b(mesh, nrays=1):
    runtimes = [Runtime()]
    mesh.isect_asm_b(runtimes, "ray_mesh_isect")
    assembler = create_assembler()
    mc = assembler.assemble(asm_code("ray_mesh_isect", mesh))
    runtime = runtimes[0]
    ds = runtime.load("test", mc)
    mesh.populate_ds(ds, mesh, "mesh1")

    bbox = mesh.bbox()
    print("Intersection bool tests begin")
    for i in range(nrays):
        ray = generate_ray(bbox)
        ray.populate_ds(ds, ray, "ray1")

        hp1 = mesh.isect_b(ray)
        runtime.run("test")

        if hp1 is False and ds['ret'] == 1:
            print(ray)
            print(hp1, ds['ret'])
            raise ValueError("Ray intersect bool error")

        if hp1 and ds['ret'] == 0:
            print(ray)
            print(hp1, ds['ret'])
            raise ValueError("Ray intersect bool error")

        if hp1 and ds['ret'] == 1:
            compare_floats(hp1, ds['t'])


#fname = 'G:/Ply_files/cube.ply'
#fname = 'F:/Ply_files/dragon_vrip_res4.ply'
#fname = 'F:/Ply_files/dragon_vrip.ply'
#fname = 'G:/Ply_files/xyzrgb_dragon.ply'
#fname = 'G:/Ply_files/lucy.ply'
#fname = 'F:/Ply_files/Horse2K.ply'
#fname = 'F:/Ply_files/Horse97K.ply'
#fname = 'F:/ray_tracing_scenes/cube/cube.obj'
fname = 'F:/ray_tracing_scenes/cube/cube_uv.obj'

start_time = time.clock()
meshes = load_meshes_from_file(fname)
print('Time to load and create(preapre) meshes from file = %f seconds' % (time.clock() - start_time,))
NRAYS = 10
NRAYS_B = 1000
for name, mesh in meshes.items():
    print("\nBegin test of mesh %s\n" % name)
    test_mesh_isect(mesh, NRAYS)
    test_mesh_isect_b(mesh, NRAYS_B)


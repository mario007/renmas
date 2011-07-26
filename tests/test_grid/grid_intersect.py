
import timeit
from tdasm import Tdasm, Runtime
import random
import renmas.utils as util
from renmas.shapes import Grid, Sphere
from renmas.core import Ray
import renmas.interface as mdl
from renmas.maths import Vector3
import renmas

def generate_ray():
    x = 7.0 
    y = 6.0 
    z = 5.5 

    dir_x = 10.0
    dir_y = 10.0
    dir_z = 10.0 

    origin = Vector3(x, y, z)
    direction = Vector3(dir_x, dir_y, dir_z)
    direction.normalize()
    ray = Ray(origin, direction)
    return ray

def random_sphere():
    x = 0.0
    y = 0.0
    z = 0.0
    radius = 3.0 
    
    v1 = Vector3(x, y, z)
    sphere = Sphere(v1, radius, 99999)

    return sphere

m_props = {"name": "m1", "sampling":"hemisphere_cos"}
m = mdl.create_material(m_props)
sh_props = {"type":"sphere", "position":(0,0,0), "radius":3, "material":"m1"}
sphere = mdl.create_shape(sh_props)
sh_props = {"type":"sphere", "position":(0,1,0), "radius":3, "material":"m1"}
sphere2 = mdl.create_shape(sh_props)
for x in range(1000):
    sh_props = {"type":"sphere", "position":(random.random(),random.random(),random.random()),
            "radius":random.random()*0.25, "material":"m1"}
    sphere3 = mdl.create_shape(sh_props)

ray = generate_ray()
#sphere = random_sphere()

hp = sphere.isect(ray)
hp = renmas.shapes.isect(ray, mdl.lst_shapes())
#print(hp.t)

grid = Grid()
grid.setup(mdl.lst_shapes())

hp3 = grid.isect(ray)
#print(hp3.t)

runtime = Runtime()
grid.isect_asm(runtime, "grid_intersect")

asm_structs = util.structs("ray", "grid", "hitpoint")
ASM = """
    #DATA
"""
ASM += asm_structs + """

    ray ray1
    hitpoint hp
    grid grid1
    float min_dist = 99999.0

    float _xmm0[4]
    float _xmm1[4]
    float _xmm2[4]
    float _xmm3[4]
    float _xmm5[4]
    float _xmm6[4]
    float _xmm7[4]
    uint32 result

    uint32 _xmm0_int[4]

    #CODE

    mov eax, ray1
    mov ebx, grid1
    mov ecx, min_dist
    mov edx, hp

    call grid_intersect

    mov dword [result], eax
    macro eq128 _xmm0 = xmm0 
    macro eq128 _xmm1 = xmm1 
    macro eq128 _xmm2 = xmm2 
    macro eq128 _xmm3 = xmm3 
    macro eq128 _xmm5 = xmm5 
    macro eq128 _xmm6 = xmm6 
    macro eq128 _xmm7 = xmm7 

    macro eq128 _xmm0_int = xmm0
    #END
"""

def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

asm = util.get_asm()
mc = asm.assemble(ASM)
#mc.print_machine_code()


ds = runtime.load("test", mc)
bbox = grid.bbox

ds["ray1.origin"] = v4(ray.origin)
ds["ray1.dir"] = (ray.dir.x, ray.dir.y, ray.dir.z, 0.0)
ds["grid1.bbox_min"] = (bbox.x0, bbox.y0, bbox.z0, 0.0)
ds["grid1.bbox_max"] = (bbox.x1, bbox.y1, bbox.z1, 0.0)
ds["grid1.n_1"] = v4(grid.n_1)
ds["grid1.one_overn"] = v4(grid.one_overn)
ds["grid1.nbox_width"] = v4(grid.nbox_width)
ds["grid1.n"] = (grid.nx, grid.ny, grid.nz, 0)
ds["grid1.grid_ptr"] = grid.asm_cells.ptr()
ds["grid1.arr_ptr"] = grid.lin_array.ptr()

runtime.run("test")

print("xmm0", ds['_xmm0'])
print("xmm1", ds['_xmm1'])
print("xmm2", ds['_xmm2'])
print("xmm3", ds['_xmm3'])
print("xmm5", ds['_xmm5'])
print("xmm6", ds['_xmm6'])
print("xmm7", ds['_xmm7'])
print("result", ds['result'])

a = ds['_xmm0_int']
print("xmm0_int=", a)
print(hex(a[0]))
print("nemoguce hp.t=", ds["hp.t"])



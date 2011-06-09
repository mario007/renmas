
from tdasm import Runtime
import renmas
import renmas.core
import renmas.samplers
import renmas.camera
import renmas.maths
import renmas.gui
import renmas.lights
import renmas.materials
import renmas.interface as ren 
import winlib
import os
import time

WIDTH = 300 
HEIGHT = 300 
NSAMPLES = 1 

def build_scene():
    s =ren.create_random_sampler(WIDTH, HEIGHT, NSAMPLES)

    ren.pinhole_camera((0.278, 0.275, -0.789), (0,0,1), 280)
    ren.create_film(WIDTH, HEIGHT, NSAMPLES)

    #create lights
    ren.create_point_light("p1", (0.3, 0.5, 0.3), (1.0, 1.0, 1.0))
    #create materials
    ren.create_lambertian("m1", 0.99, 0.0, 0.0)
    ren.create_lambertian("m2", 0.7, 0.7, 0.7)
    ren.create_lambertian("m3", 0.0, 0.99, 0.0)
    ren.create_lambertian("m4", 0.0, 0.0, 0.99)
    ren.create_lambertian("m5", 0.99, 0.0, 0.99)
    ren.create_lambertian("m6", 0.0, 0.77, 0.0)
    #create shapes

    #create triangles for cornell
    ## FLOOR
    idx = ren.get_mat_idx("m2")
    ren.create_triangle((0.556, 0.0, 0.0), (0.006, 0.0, 0.559), (0.556, 0.0, 0.559), idx)
    ren.create_triangle((0.006, 0.0, 0.559), (0.556, 0.0, 0.0), (0.003, 0.0, 0.0), idx)
    ## BACK WALL
    idx = ren.get_mat_idx("m1")
    ren.create_triangle((0.556, 0.0, 0.559), (0.000, 0.549, 0.559), (0.556, 0.549, 0.559), idx)
    ren.create_triangle((0.000, 0.549, 0.559), (0.556, 0.0, 0.559), (0.006, 0.0, 0.559), idx)

    ## RIGHT WALL
    idx = ren.get_mat_idx("m3")
    ren.create_triangle((0.006, 0.0, 0.559), (0.00, 0.549, 0.00), (0.0, 0.549, 0.559), idx)
    ren.create_triangle((0.000, 0.549, 0.0), (0.006, 0.0, 0.559), (0.003, 0.0, 0.0), idx)

    ## LEFT WALL
    idx = ren.get_mat_idx("m4")
    ren.create_triangle((0.556, 0.0, 0.0), (0.556, 0.549, 0.559), (0.556, 0.549, 0.0), idx)
    ren.create_triangle((0.556, 0.549, 0.559), (0.556, 0.0, 0.0), (0.556, 0.0, 0.559), idx)

    ## TOP
    idx = ren.get_mat_idx("m5")
    ren.create_triangle((0.556, 0.549, 0.559), (0.0, 0.549, 0.0), (0.556, 0.549, 0.0), idx)
    ren.create_triangle((0.0, 0.549, 0.0), (0.556, 0.549, 0.559), (0.0, 0.549, 0.559), idx)

    ## gornji dio manje kocke
    idx = ren.get_mat_idx("m5")
    ren.create_triangle((0.474, 0.165, 0.225), (0.426, 0.165, 0.065), (0.316, 0.165, 0.272), idx)
    ren.create_triangle((0.266, 0.165, 0.114), (0.316, 0.165, 0.272), (0.426, 0.165, 0.065), idx)

    idx = ren.get_mat_idx("m5")
    ren.create_triangle((0.266, 0.0, 0.114), (0.266, 0.165, 0.114), (0.316, 0.165, 0.272), idx)
    ren.create_triangle((0.316, 0.0, 0.272), (0.266, 0.0, 0.114), (0.316, 0.165, 0.272), idx)

    idx = ren.get_mat_idx("m5")
    ren.create_triangle((0.316, 0.0, 0.272), (0.316, 0.165, 0.272), (0.474, 0.165, 0.225), idx)
    ren.create_triangle((0.474, 0.165, 0.225), (0.316, 0.0, 0.272), (0.474, 0.0, 0.225), idx)

    idx = ren.get_mat_idx("m5")
    ren.create_triangle((0.474, 0.0, 0.225), (0.474, 0.165, 0.225), (0.426, 0.165, 0.065), idx)
    ren.create_triangle((0.426, 0.165, 0.065), (0.426, 0.0, 0.065), (0.474, 0.0, 0.225), idx)

    idx = ren.get_mat_idx("m5")
    ren.create_triangle((0.426, 0.0, 0.065), (0.426, 0.165, 0.065), (0.266, 0.165, 0.114), idx)
    ren.create_triangle((0.266, 0.165, 0.114), (0.266, 0.0, 0.114), (0.426, 0.0, 0.065), idx)

    #veca kocka - gornji dio
    idx = ren.get_mat_idx("m6")
    ren.create_triangle((0.133, 0.330, 0.247), (0.291, 0.330, 0.296), (0.242, 0.330, 0.456), idx)
    ren.create_triangle((0.242, 0.330, 0.456), (0.084, 0.330, 0.406), (0.133, 0.330, 0.247), idx)

    idx = ren.get_mat_idx("m6")
    ren.create_triangle((0.133, 0.0, 0.247), (0.133, 0.330, 0.247), (0.084, 0.330, 0.406), idx)
    ren.create_triangle((0.084, 0.330, 0.406), (0.084, 0.0, 0.406), (0.133, 0.0, 0.247), idx)

    idx = ren.get_mat_idx("m6")
    ren.create_triangle((0.084, 0.000, 0.406), (0.084, 0.330, 0.406), (0.242, 0.330, 0.456), idx)
    ren.create_triangle((0.242, 0.330, 0.456), (0.242, 0.000, 0.456), (0.084, 0.000, 0.406), idx)

    idx = ren.get_mat_idx("m6")
    ren.create_triangle((0.242, 0.000, 0.456), (0.242, 0.330, 0.456), (0.291, 0.330, 0.296), idx)
    ren.create_triangle((0.291, 0.330, 0.296), (0.291, 0.000, 0.296), (0.242, 0.000, 0.456), idx)

    idx = ren.get_mat_idx("m6")
    ren.create_triangle((0.291, 0.000, 0.296), (0.291, 0.330, 0.296), (0.133, 0.330, 0.247), idx)
    ren.create_triangle((0.133, 0.330, 0.247), (0.133, 0.000, 0.247), (0.291, 0.000, 0.296), idx)

    

asm_structs = renmas.utils.structs("sample", "ray", "hitpoint")
ASM = """
#DATA
"""
ASM += asm_structs + """
    sample sam
    ray r1
    hitpoint hp
    uint32 end_sam
    uint32 hit

#CODE
    pocetak:
    mov dword [end_sam], 1
    mov eax, sam
    call get_sample
    cmp eax, 0
    je _end_sampling
    
    ; now we must calculate ray
    mov eax, r1
    mov ebx, sam 
    call generate_ray

    ; now intersect ray with shapes
    ; eax = pointer_to_ray, ebx = pointer_to_hitpoint
    mov eax, r1
    mov ebx, hp
    call scene_isect 
    mov dword [hit], eax

    jmp pocetak

    _end_sampling:
    mov dword [end_sam], 0
#END
"""

build_scene()

sampler = ren.get_sampler()
sampler.tile(0, 0, WIDTH, HEIGHT)
camera = ren.get_camera()

def get_runtime():
    runtime = Runtime()
    sampler.get_sample_asm(runtime, "get_sample")
    camera.ray_asm(runtime, "generate_ray")

    dyn_arrays = ren.dyn_arrays()
    renmas.shapes.linear_isect_asm(runtime, "scene_isect", dyn_arrays)
    return runtime

runtime = get_runtime()
asm = renmas.utils.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("raycast", mc)

start = time.clock()
runtime.run("raycast")
end = time.clock()
print(end - start)


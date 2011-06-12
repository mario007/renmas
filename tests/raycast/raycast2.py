
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

blitter = renmas.gui.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)


WIDTH = 300 
HEIGHT = 300 
NSAMPLES = 1 

lst_tiles = ren.get_tiles(WIDTH, HEIGHT, NSAMPLES)
ntile = -1 
def next_tile():
    global ntile
    if ntile == len(lst_tiles) - 1:
        return None
    ntile += 1
    return lst_tiles[ntile]

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

    # RIGHT WALL
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


build_scene()
isect = renmas.shapes.isect #intersection rutine

#ALGORIHM RayCast

background = renmas.core.Spectrum(0.05, 0.05, 0.05) 
hp2 = renmas.shapes.HitPoint()
hp2.spectrum = background

sampler = ren.get_sampler()
camera = ren.get_camera()
film = ren.get_film()
lst_lights = ren.lst_lights()
shapes = ren.lst_shapes()

def get_runtime():
    runtime = Runtime()
    sampler.get_sample_asm(runtime, "get_sample")
    camera.ray_asm(runtime, "generate_ray")

    dyn_arrays = ren.dyn_arrays()
    renmas.shapes.linear_isect_asm(runtime, "scene_isect", dyn_arrays)
    return runtime

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
    #END

    _end_sampling:
    mov dword [end_sam], 0
#END
"""

runtime = get_runtime()
asm = renmas.utils.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("raycast", mc)

def get_v3(ds, name):
    x, y, z, w = ds[name]
    return renmas.maths.Vector3(x, y, z)

def get_hp_asm(sample):
    runtime.run("raycast")
    end = ds["end_sam"]
    if end == 0: return False
    sample.ix = ds["sam.ix"]
    sample.iy = ds["sam.iy"]

    hit = ds["hit"]
    if hit == 0: return None

    hp_new = renmas.shapes.HitPoint()
    hp_new.wo = get_v3(ds, "r1.dir") * -1.0
    hp_new.t = ds["hp.t"]
    hp_new.hit_point = get_v3(ds, "hp.hit")
    hp_new.normal = get_v3(ds, "hp.normal")
    hp_new.material = ds["hp.mat_index"]

    x, y, tem1, tem2 = ds["sam.xyxy"]
    sample.x = x
    sample.y = y

    return hp_new 

def get_hp(sample):
    sam = sampler.get_sample(sample)
    if sam is None: return False 
    ray = camera.ray(sample)
    hp = isect(ray, shapes, 999999.0)
    if hp is not None:
        hp.wo = ray.dir * -1.0
    return hp 

duration = 0.0
def raycast():
    tile = next_tile()
    if tile is None: 
        return None
    sample = renmas.samplers.Sample()
    sample4 = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)
    start = time.clock()
    while True:
        #hp = get_hp(sample)
        if sample.ix == 6 and sample.iy == 911:
            print("hit", hp.hit_point)
            print("normal =",hp.normal)
        hp = get_hp_asm(sample)

        if hp is False: break
        #if hp4 is None and hp is not None:
        #   print("Tu je jedna greska", sample.ix, sample.iy, hp.normal, hp.t)
        #if hp4 is not None and hp is None:
        #    print("Tu je druga greska.", sample.ix, sample.iy)
        if hp is None:
            film.add_sample(sample, hp2) #background
        else:
            shade(sample, hp)
            film.add_sample(sample, hp) 

    blt_float_img_to_window(0, 0, film.image, win)
    end = time.clock()
    global duration
    duration = duration + (end - start)
    print("Renderiranje jednog tile je trajalo", end - start, duration)
    return True

def shade(sample, hp):
    #loop through lights
    tmp_spec = renmas.core.Spectrum(0.0, 0.0, 0.0)
    for light in lst_lights:
        if light.L(hp) is True: #light is visible
            #mat1.brdf(hp)
            ren.get_material(hp.material).brdf(hp)
            tmp_spec = tmp_spec + hp.spectrum
            #hp.spectrum = hp.spectrum * hp.ndotwi
    hp.spectrum = tmp_spec


win = renmas.gui.MainWindow(500, 500, "Test")
win.redraw()
win.render_handler(raycast)
winlib.MainLoop()



import winlib
import renmas.gui 
import renmas
import renmas.core
import renmas.samplers
import renmas.camera
import renmas.maths
import renmas.lights
import renmas.materials
import renmas.interface as ren 
import os
import time
from tdasm import Runtime
from scenes import cornell_scene


blitter = renmas.gui.Blitter()
def blt_float_img_to_window(x, y, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

def save_image(film, name):
    blitter = renmas.gui.Blitter()

    wid, he = film.image.get_size()
    img = renmas.gui.ImageRGBA(wid, he)


    dw, dh = img.get_size()
    da, dpitch = img.get_addr()
    sw, sh = film.image.get_size()
    sa, spitch = film.image.get_addr()
    blitter.blt_floatTorgba(da, 0, 0, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)
    renmas.gui.save_image(name, img)
    return None

def build_scene2():
    s_props = {"type":"random", "pixel":0.8, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(0.278, 0.275, -0.789), "lookat":(0,0,1), "distance":380}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    #create lights
    l_props = {"type":"point", "name": "light1", "position":(0.2,0.5,0.2), "spectrum":(0.99,0.99,0.99)}
    l = ren.create_light(l_props)


    m_props = {"type":"lambertian", "R":(0.99, 0.0, 0.0)}
    m = ren.create_material("m1")
    ren.add_brdf("m1", m_props)

    m_props = {"type":"lambertian", "R":(0.00, 0.99, 0.0)}
    m = ren.create_material("m2")
    ren.add_brdf("m2", m_props)

    m_props = {"type":"lambertian", "R":(0.00, 0.00, 0.99)}
    m = ren.create_material("m3")
    ren.add_brdf("m3", m_props)

    m_props = {"type":"lambertian", "R":(0.00, 0.99, 0.99)}
    m = ren.create_material("m4")
    ren.add_brdf("m4", m_props)

    m_props = {"type":"lambertian", "R":(0.99, 0.0, 0.99)}
    m = ren.create_material("m5")
    ren.add_brdf("m5", m_props)

    m_props = {"type":"lambertian", "R":(0.99, 0.99, 0.00)}
    m = ren.create_material("m6")
    ren.add_brdf("m6", m_props)

    m_props = {"type":"lambertian", "R":(0.55, 0.22, 0.88)}
    m = ren.create_material("m7")
    ren.add_brdf("m7", m_props)

    #create triangles for cornell
    ## FLOOR
    sh_props = {"type":"triangle", "p0":(0.556,0.0,0.0), "p1":(0.006, 0.0, 0.559), "p2":(0.556, 0.0, 0.559) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.006,0.0,0.559), "p1":(0.556, 0.0, 0.0), "p2":(0.003, 0.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    ## BACK WALL
    sh_props = {"type":"triangle", "p0":(0.556,0.0,0.559), "p1":(0.0, 0.549, 0.559), "p2":(0.556, 0.549, 0.559) ,"material":"m2"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.0,0.549,0.559), "p1":(0.556, 0.0, 0.559), "p2":(0.006, 0.0, 0.559) ,"material":"m2"}
    s = ren.create_shape(sh_props)
    # RIGHT WALL
    sh_props = {"type":"triangle", "p0":(0.006,0.0,0.559), "p1":(0.0, 0.549, 0.0), "p2":(0.0, 0.549, 0.559) ,"material":"m3"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.0,0.549,0.0), "p1":(0.006, 0.0, 0.559), "p2":(0.003, 0.0, 0.0) ,"material":"m3"}
    s = ren.create_shape(sh_props)
    ## LEFT WALL
    sh_props = {"type":"triangle", "p0":(0.556,0.0,0.0), "p1":(0.556, 0.549, 0.559), "p2":(0.556, 0.549, 0.0) ,"material":"m4"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.556,0.549,0.559), "p1":(0.556, 0.0, 0.0), "p2":(0.556, 0.0, 0.559) ,"material":"m4"}
    s = ren.create_shape(sh_props)
    ## TOP
    sh_props = {"type":"triangle", "p0":(0.556,0.549,0.559), "p1":(0.0, 0.549, 0.0), "p2":(0.556, 0.549, 0.0) ,"material":"m5"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.0,0.549,0.0), "p1":(0.556, 0.549, 0.559), "p2":(0.0, 0.549, 0.559) ,"material":"m5"}
    s = ren.create_shape(sh_props)

    #veca kocka - gornji dio
    sh_props = {"type":"triangle", "p0":(0.133,0.330,0.247), "p1":(0.291, 0.330, 0.296), "p2":(0.242, 0.330, 0.456) ,"material":"m6"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.242,0.330,0.456), "p1":(0.084, 0.330, 0.406), "p2":(0.133, 0.330, 0.247) ,"material":"m6"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.133,0.000,0.247), "p1":(0.133, 0.330, 0.247), "p2":(0.084, 0.330, 0.406) ,"material":"m6"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.084,0.330,0.406), "p1":(0.084, 0.000, 0.406), "p2":(0.133, 0.000, 0.247) ,"material":"m6"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.084,0.000,0.406), "p2":(0.084, 0.330, 0.406), "p1":(0.242, 0.330, 0.456) ,"material":"m6"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.242,0.330,0.456), "p2":(0.242, 0.000, 0.456), "p1":(0.084, 0.000, 0.406) ,"material":"m6"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.242,0.000,0.456), "p1":(0.242, 0.330, 0.456), "p2":(0.291, 0.330, 0.296) ,"material":"m6"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.291,0.330,0.296), "p1":(0.291, 0.000, 0.296), "p2":(0.242, 0.000, 0.456) ,"material":"m6"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.291,0.000,0.296), "p2":(0.291, 0.330, 0.296), "p1":(0.133, 0.330, 0.247) ,"material":"m6"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.133,0.330,0.247), "p2":(0.133, 0.000, 0.247), "p1":(0.291, 0.000, 0.296) ,"material":"m6"}
    s = ren.create_shape(sh_props)

    ## gornji dio manje kocke
    sh_props = {"type":"triangle", "p0":(0.474,0.165,0.225), "p1":(0.426, 0.165, 0.065), "p2":(0.316, 0.165, 0.272) ,"material":"m7"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.266,0.165,0.114), "p1":(0.316, 0.165, 0.272), "p2":(0.426, 0.165, 0.065) ,"material":"m7"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.266,0.00,0.114), "p1":(0.266, 0.165, 0.114), "p2":(0.316, 0.165, 0.272) ,"material":"m7"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.316,0.00,0.272), "p1":(0.266, 0.000, 0.114), "p2":(0.316, 0.165, 0.272) ,"material":"m7"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.316,0.000,0.272), "p1":(0.316, 0.165, 0.272), "p2":(0.474, 0.165, 0.225) ,"material":"m7"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.474,0.165,0.225), "p1":(0.316, 0.000, 0.272), "p2":(0.474, 0.000, 0.225) ,"material":"m7"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.474,0.000,0.225), "p1":(0.474, 0.165, 0.225), "p2":(0.426, 0.165, 0.065) ,"material":"m7"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.426,0.165,0.065), "p1":(0.426, 0.000, 0.065), "p2":(0.474, 0.000, 0.225) ,"material":"m7"}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"triangle", "p0":(0.436,0.000,0.065), "p1":(0.426, 0.165, 0.065), "p2":(0.266, 0.165, 0.114) ,"material":"m7"}
    s = ren.create_shape(sh_props)
    sh_props = {"type":"triangle", "p0":(0.266,0.165,0.114), "p1":(0.266, 0.000, 0.114), "p2":(0.426, 0.000, 0.065) ,"material":"m7"}
    s = ren.create_shape(sh_props)

def build_scene():
    s_props = {"type":"random", "pixel":1.0, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(5, 6.5, 7.7), "lookat":(0,0,0), "distance":480}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    l_props = {"type":"point", "name": "light1", "position":(6,7,9), "spectrum":(2.99,2.99,2.99)}
    l = ren.create_light(l_props)

    m_props = {"type":"phong", "R":(0.22, 0.63, 0.53), "e": 12.2, "k":0.3}
    m = ren.create_material("m1")
    ren.add_brdf("m1", m_props)

    m_props = {"type":"lambertian", "R":(0.22, 0.63, 0.53), "k":0.6}
    ren.add_brdf("m1", m_props)

    sh_props = {"type":"sphere", "position":(0,0,0), "radius":2, "material":"m1"}
    s = ren.create_shape(sh_props)

cornell_scene()
#v1 = renmas.maths.Vector3(55.28, 47.657430, 43.70494)
#v2 = renmas.maths.Vector3(25.0, 50.0, 25.0)
#ret = renmas.shapes.visible(v1, v2)
#print(ret)

lst_tiles = ren.tiles()
ntile = -1 
def next_tile():
    global ntile
    if ntile == len(lst_tiles) - 1:
        return None
    ntile += 1
    return lst_tiles[ntile]
image_saved = False
duration = 0.0

grid = renmas.shapes.Grid()
grid.setup(ren.lst_shapes())

def raycast():
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()
    lst_lights = ren.lst_lights()
    shapes = ren.lst_shapes()
    #isect = renmas.shapes.isect #intersection rutine
    isect = grid.intersect
    shade = renmas.core.shade

    background = renmas.core.Spectrum(0.00, 0.00, 0.00) 
    hp2 = renmas.shapes.HitPoint()
    hp2.spectrum = background

    tile = next_tile()
    if tile is None: 
        global image_saved
        if not image_saved:
            save_image(film, "Image5.png")
            print("Slika je spremljena")
            image_saved = True
        return None
    sample = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)
    start = time.clock()
    
    while True:
        sam = sampler.get_sample(sample)
        if sam is None: break 
        ray = camera.ray(sample)
        #hp = isect(ray, shapes, 999999.0)
        hp = isect(ray)

        if sample.ix == 10 and sample.iy == 1650:
            print(hp.hit_point)
            print(sample.ix, sample.iy, hp.spectrum)
            #import pdb; pdb.set_trace()

        if hp is None:
            film.add_sample(sample, hp2) #background
        else:
            hp.wo = ray.dir * -1.0
            shade(hp)
            film.add_sample(sample, hp) #background

    blt_float_img_to_window(0, 0, film.image, win)
    end = time.clock()
    global duration
    duration = duration + (end - start)
    print("Renderiranje jednog tile je trajalo", end - start, duration)
    return True

asm_structs = renmas.utils.structs("sample", "ray", "hitpoint")
ASM = """
#DATA
"""
ASM += asm_structs + """
    sample sam
    ray r1
    hitpoint hp
    hitpoint background
    uint32 end_sam
    float back[4] = 0.00, 0.00, 0.00, 0.00
    float minus_one[4] = -1.0, -1.0, -1.0, 0.0

#CODE
    macro eq128 background.spectrum = back

    _next_sample:
    ; put pointer to sample structre in eax and generate sample
    mov eax, sam
    call get_sample
    ; test to si if we are done sampling picture 
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

    ;if ray hit some object we must calculate shading
    ; in eax is result of intersection routine
    cmp eax, 0
    je _background


    ; call shading routine
    mov eax, hp
    mov ebx, r1
    macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one 
    call shade
    ; add_sample to film
    mov eax, hp
    mov ebx, sam 
    call add_sample
    jmp _next_sample

    _background: ; add background sample to film
    mov eax, background
    mov ebx, sam
    call add_sample

    jmp _next_sample

    
    _end_sampling:
    mov dword [end_sam], 0
#END
"""
runtime = Runtime()
ren.get_sampler().get_sample_asm(runtime, "get_sample")
ren.get_camera().ray_asm(runtime, "generate_ray")
renmas.shapes.linear_isect_asm(runtime, "scene_isect", ren.dyn_arrays())
renmas.shapes.visible_asm(runtime, "visible", "scene_isect")
renmas.core.generate_shade(runtime, "shade", "visible")
ren.get_film().add_sample_asm(runtime, "add_sample")

asm = renmas.utils.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("raycast", mc)

def raycast_asm():
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()
    lst_lights = ren.lst_lights()
    shapes = ren.lst_shapes()
    isect = renmas.shapes.isect #intersection rutine
    shade = renmas.core.shade

    background = renmas.core.Spectrum(0.05, 0.05, 0.05) 
    hp2 = renmas.shapes.HitPoint()
    hp2.spectrum = background

    tile = next_tile()
    if tile is None: 
        global image_saved
        if not image_saved:
            save_image(film, "Image5.png")
            image_saved = True
        return None
    sample = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)
    start = time.clock()

    runtime.run("raycast") #100% rendering in assembly language

    blt_float_img_to_window(0, 0, film.image, win)
    end = time.clock()
    global duration
    duration = duration + (end - start)
    print("Renderiranje jednog tile je trajalo", end - start, duration)
    return True

win = renmas.gui.MainWindow(600, 400, "Test")
win.redraw()
#win.render_handler(raycast_asm)
win.render_handler(raycast)
winlib.MainLoop()


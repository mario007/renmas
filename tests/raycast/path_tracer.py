
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

WIDTH = 600 
HEIGHT = 600 
NSAMPLES = 32 

lst_tiles = ren.get_tiles(WIDTH, HEIGHT, NSAMPLES)
ntile = -1 
def next_tile():
    global ntile
    if ntile == len(lst_tiles) - 1:
        return None
    ntile += 1
    return lst_tiles[ntile]

def build_scene3():
    s_props = {"type":"random", "pixel":0.5, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(27.6, 27.4, -80), "lookat":(27.6, 27.4, 0.0), "distance":400}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    #area light
    l_props = {"type":"area", "spectrum":(55.99, 55.99, 55.99), "shape":"rectangle", "p":(21.3, 54.87999, 22.7),
            "edge_a":(0.0, 0.0, 10.5), "edge_b":(13.0, 0.0, 0.0), "normal":(0.0, -1.0, 0.0)}
    l = ren.create_light(l_props)

    m_props = {"name": "m1", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.6, 0.6, 0.6)} # back wall - white wall
    ren.add_brdf("m1", m_props)

    m_props = {"name": "m2", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.342, 0.015, 0.015)} # left wall- red wall
    ren.add_brdf("m2", m_props)

    m_props = {"name": "m3", "sampling": "hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.222, 0.354, 0.12)} # right wall- green wall
    ren.add_brdf("m3", m_props)

    #back wall
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 55.92), "edge_a":(55.28, 0.0, 0.0), "edge_b":(0.0, 54.88, 0.0), "normal":(0.0, 0.0, -1.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    #left wall
    sh_props = {"type":"rectangle", "p":(55.28, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(0.0, 54.88, 0.0), "normal":(-1.0, 0.0, 0.0) ,"material":"m2"}
    s = ren.create_shape(sh_props)

    #right wall
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(0.0, 54.88, 0.0), "normal":(1.0, 0.0, 0.0) ,"material":"m3"}
    s = ren.create_shape(sh_props)

    #floor
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(55.28, 0.0, 0.0), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    #ceiling
    sh_props = {"type":"rectangle", "p":(0.0, 54.88, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(55.28, 0.0, 0.0), "normal":(0.0, -1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    # short box
    #top
    sh_props = {"type":"rectangle", "p":(13.0, 16.5, 6.5), "edge_a":(-4.8, 0.0, 16.0), "edge_b":(16.0, 0.0, 4.9), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 1
    sh_props = {"type":"rectangle", "p":(13.0, 0.0, 6.5), "edge_a":(-4.8, 0.0, 16.0), "edge_b":(0.0, 16.5, 0.0), "normal":(-0.957826, 0.0, -0.28734) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 2
    sh_props = {"type":"rectangle", "p":(8.2, 0.0, 22.5), "edge_a":(15.8, 0.0, 4.7), "edge_b":(0.0, 16.5, 0.0), "normal":(-0.28512, 0.0, 0.95489) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 3
    sh_props = {"type":"rectangle", "p":(24.2, 0.0, 27.4), "edge_a":(4.8, 0.0, -16.0), "edge_b":(0.0, 16.5, 0.0), "normal":(-0.95782, 0.0, -0.28734) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 4
    sh_props = {"type":"rectangle", "p":(29, 0.0, 11.4), "edge_a":(-16.0, 0.0, -4.9), "edge_b":(0.0, 16.5, 0.0), "normal":(-0.292825, 0.0, -0.95616) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    # tall box
    #top
    sh_props = {"type":"rectangle", "p":(42.3, 33.0, 24.7), "edge_a":(-15.8, 0.0, 4.9), "edge_b":(4.9, 0.0, 15.9), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 1
    sh_props = {"type":"rectangle", "p":(42.3, 0.0, 24.7), "edge_a":(-15.8, 0.0, 4.9), "edge_b":(0.0, 33.0, 0.0), "normal":(0.2962, 0.0, 0.955123) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 2
    sh_props = {"type":"rectangle", "p":(26.5, 0.0, 29.6), "edge_a":(4.9, 0.0, 15.9), "edge_b":(0.0, 33.0, 0.0), "normal":(0.955648, 0.0, -0.2945) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 3
    sh_props = {"type":"rectangle", "p":(31.4, 0.0, 45.5), "edge_a":(15.8, 0.0, -4.9), "edge_b":(0.0, 33.0, 0.0), "normal":(-0.2962, 0.0, -0.955123) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 4
    sh_props = {"type":"rectangle", "p":(47.2, 0.0, 40.6), "edge_a":(-4.9, 0.0, -15.9), "edge_b":(0.0, 33.0, 0.0), "normal":(-0.95564, 0.0, 0.2945) ,"material":"m1"}
    s = ren.create_shape(sh_props)

def build_scene():
    s_props = {"type":"random", "pixel":1.0, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(5, 6.5, 7.7), "lookat":(0,0,0), "distance":480}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    l_props = {"type":"point", "name": "light1", "position":(6,7,9), "spectrum":(0.99,0.99,0.99)}
    l = ren.create_light(l_props)

    m_props = {"type":"phong", "R":(0.99, 0.99, 0.99), "e": 20.2, "k":0.5}
    m = ren.create_material("m1")
    ren.add_brdf("m1", m_props)

    m_props = {"type":"lambertian", "R":(0.22, 0.63, 0.53), "k":0.8}
    ren.add_brdf("m1", m_props)

    sh_props = {"type":"sphere", "position":(0,0,0), "radius":2, "material":"m1"}
    s = ren.create_shape(sh_props)

build_scene3()

image_saved = False
duration = 0.0
def raycast():
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()
    lst_lights = ren.lst_lights()
    shapes = ren.lst_shapes()
    isect = renmas.shapes.isect #intersection rutine
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
        hp = isect(ray, shapes, 999999.0)

        if hp is None:
            hp2.spectrum = background
            film.add_sample(sample, hp2) #background
            continue
        else:
            hp.wo = ray.dir * -1.0
            shade(hp)

        #emissive -- stop
        #TODO

        #first depth
        o = hp.hit_point
        d = hp.wi
        kr = hp.brdf * (1.0 / hp.pdf) * hp.ndotwi
        ray1 = renmas.core.Ray(o, d)

        s = hp.spectrum
        spec = renmas.core.Spectrum(s.r, s.g, s.b)

        hp = isect(ray1, shapes, 999999.0)
        if hp is None:
            #spec2 = spec + kr.mix_spectrum(background)
            spec2 = spec 
            hp2.spectrum = spec2
            film.add_sample(sample, hp2) #background
            continue
        else:
            hp.wo = ray.dir * -1.0
            shade(hp)

            spec2 = spec + hp.spectrum.mix_spectrum(kr)
            hp.spectrum = spec2
            film.add_sample(sample, hp) 


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
    float kr[4]
    float spec1[4]

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
    ;mov eax, hp
    ;mov ebx, sam 
    ;call add_sample
    jmp _depth1

    _background: ; add background sample to film
    mov eax, background
    mov ebx, sam
    call add_sample
    jmp _next_sample

    _depth1:
    mov eax, r1
    mov ebx, hp
    macro eq128 eax.ray.origin = ebx.hitpoint.hit 
    macro eq128 eax.ray.dir = ebx.hitpoint.wi
    macro eq32 xmm0 = ebx.hitpoint.ndotwi 
    macro eq32 xmm1 = ebx.hitpoint.pdf
    macro eq32 xmm0 = xmm0 / xmm1
    macro broadcast xmm0 = xmm0[0]
    macro eq128 xmm0 = xmm0 * ebx.hitpoint.brdf
    macro eq128 kr = xmm0
    macro eq128 spec1 = ebx.hitpoint.spectrum

    call scene_isect 
    cmp eax, 0
    je _background1
    ; call shading routine
    mov eax, hp
    mov ebx, r1
    macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one 
    call shade

    ; add_sample to film
    mov eax, hp
    mov ebx, sam 
    macro eq128 xmm0 = eax.hitpoint.spectrum * kr
    macro eq128 xmm0 = xmm0 + spec1
    macro eq128 eax.hitpoint.spectrum = xmm0
    call add_sample

    jmp _next_sample

    _background1:
    mov eax, hp
    macro eq128 eax.hitpoint.spectrum = spec1
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

win = renmas.gui.MainWindow(800, 600, "Test")
win.redraw()
#win.render_handler(raycast_asm)
win.render_handler(raycast)
winlib.MainLoop()
pass
#print("Prije pucanja")


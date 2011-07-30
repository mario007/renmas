
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

from scenes import cornell_scene, dragon

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

def build_scene():
    s_props = {"type":"random", "pixel":2.0, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(5, 6.5, 7.7), "lookat":(0,0,0), "distance":480}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    l_props = {"type":"point", "name": "light1", "position":(6,7,9), "spectrum":(0.99,0.99,0.99)}
    l = ren.create_light(l_props)

    m_props = {"name": "m1", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"phong", "R":(0.99, 0.99, 0.99), "e": 20.2, "k":0.5}
    ren.add_brdf("m1", m_props)

    m_props = {"type":"lambertian", "R":(0.22, 0.63, 0.53), "k":1.0}
    ren.add_brdf("m1", m_props)

    sh_props = {"type":"sphere", "position":(0,0,0), "radius":2, "material":"m1"}
    s = ren.create_shape(sh_props)

#cornell_scene()
dragon()

#build_scene()
ren.prepare_for_rendering()

lst_tiles = ren.tiles()
ntile = -1 
def next_tile():
    global ntile
    if ntile == len(lst_tiles) - 1:
        return None
    ntile += 1
    return lst_tiles[ntile]

def calc_brdf(hp, ray):
    hp.wo = ray.dir * -1.0
    renmas.core.shade(hp)

    o = hp.hit_point
    d = hp.wi
    kr = hp.brdf * (1.0 / hp.pdf) * hp.ndotwi
    ray.dir = d
    ray.origin = o

    s = hp.spectrum
    spec = renmas.core.Spectrum(s.r, s.g, s.b)
    return (spec, kr)

image_saved = False
duration = 0.0
def raycast():
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()
    lst_lights = ren.lst_lights()

    shapes = ren.isect_shapes()
    isect = renmas.shapes.isect #intersection rutine
    shade = renmas.core.shade
    recursion_depth = 3

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

        Ld1, Brdf1 = calc_brdf(hp, ray)
        hp = isect(ray, shapes, 999999.0)
        if hp is None:
            hp2.spectrum = Ld1 
            film.add_sample(sample, hp2) 
            continue

        Ld2, Brdf2 = calc_brdf(hp, ray)
        hp = isect(ray, shapes, 999999.0)
        if hp is None:
            hp2.spectrum = Ld1 + Ld2.mix_spectrum(Brdf1)
            film.add_sample(sample, hp2) 
            continue

        Ld3, Brdf3 = calc_brdf(hp, ray)
        spectrum = Ld3.mix_spectrum(Brdf2) + Ld2
        spectrum = spectrum.mix_spectrum(Brdf1) + Ld1
        hp.spectrum = spectrum 
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

    float Ld1[4]
    float Ld2[4]
    float Ld3[4]
    float Brdf1[4]
    float Brdf2[4]
    float Brdf3[4]
    float test_brdf[4] = 0.3, 0.5, 0.1, 0.0 

#CODE
    macro eq128 background.spectrum = back

    _next_sample:
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

    mov eax, hp
    mov ebx, r1
    call calc_brdf
    ; xmm0 = Ld xmm1 = Brdf
    macro eq128 Ld1 = xmm0
    macro eq128 Brdf1 = xmm1
    mov eax, r1
    mov ebx, hp
    call scene_isect
    cmp eax, 0
    je _depth1
    
    mov eax, hp
    mov ebx, r1
    call calc_brdf
    macro eq128 Ld2 = xmm0
    macro eq128 Brdf2 = xmm1
    mov eax, r1
    mov ebx, hp
    call scene_isect
    cmp eax, 0
    je _depth2

    mov eax, hp
    mov ebx, r1
    call calc_brdf
    macro eq128 Ld3 = xmm0
    macro eq128 Brdf3 = xmm1
    mov eax, r1
    mov ebx, hp
    call scene_isect
    cmp eax, 0
    jmp _depth3

    _background: ; add background sample to film
    mov eax, background
    mov ebx, sam
    call add_sample
    jmp _next_sample


    ; add_sample to film
    _depth1:
    mov eax, hp
    mov ebx, sam 
    macro eq128 eax.hitpoint.spectrum = Ld1 
    call add_sample

    jmp _next_sample
    
    _depth2:
    mov eax, hp
    mov ebx, sam 
    macro eq128 xmm0 = Ld2 * Brdf1 
    macro eq128 eax.hitpoint.spectrum = xmm0 + Ld1
    call add_sample

    jmp _next_sample

    _depth3:
    mov eax, hp
    mov ebx, sam 
    macro eq128 xmm0 = Ld3 * Brdf2 
    macro eq128 xmm0 = xmm0 + Ld2
    macro eq128 xmm0 = xmm0 * Brdf1
    macro eq128 eax.hitpoint.spectrum = xmm0 + Ld1
    call add_sample

    jmp _next_sample

    _end_sampling:
    mov dword [end_sam], 0
    #END

    ; eax - pointer to hp, ebx - pointer to ray 
    ; result  xmm0 - Ld  xmm1 - brdf
    calc_brdf:
    push eax
    push ebx
    ; call shading routine
    macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one 
    call shade
    pop eax 
    pop ebx 

    macro eq128 eax.ray.origin = ebx.hitpoint.hit 
    macro eq128 eax.ray.dir = ebx.hitpoint.wi

    macro eq32 xmm1 = ebx.hitpoint.ndotwi 
    macro eq32 xmm0 = ebx.hitpoint.pdf
    macro eq32 xmm1 = xmm1 / xmm0
    macro broadcast xmm1 = xmm1[0]
    macro eq128 xmm1 = xmm1 * ebx.hitpoint.brdf
    macro eq128 xmm0 = ebx.hitpoint.spectrum

    ret
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


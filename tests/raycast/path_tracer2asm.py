
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
from scenes import cornell_scene, dragon, sphere

dragon()
#cornell_scene()
#sphere()


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
    float back[4] = 0.40, 0.40, 0.40, 0.99
    float background1[4] = 0.99, 0.99, 0.99, 0.00
    float minus_one[4] = -1.0, -1.0, -1.0, 0.0
    float one[4] = 1.0, 1.0, 1.0, 1.0
    float zero[4] = 0.0, 0.0, 0.0, 0.0

    float transmitance = 1.0
    uint32 max_depth = 4
    uint32 cur_depth = 0
    float Ld[40] ;this is for maxdepth of 10
    float Lr[40]
    float epsilon = 0.02

#CODE
    macro eq128 background.spectrum = back 

    _next_sample:
    macro eq32 transmitance = one

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
    mov eax, r1
    mov ebx, hp
    macro eq128 eax.ray.origin = ebx.hitpoint.hit 
    macro eq128 eax.ray.dir = ebx.hitpoint.wi

    macro eq32 xmm1 = ebx.hitpoint.ndotwi 
    macro eq32 xmm0 = ebx.hitpoint.pdf
    macro eq32 xmm1 = xmm1 / xmm0
    macro broadcast xmm1 = xmm1[0]
    macro eq128 xmm1 = xmm1 * ebx.hitpoint.brdf
    macro eq128 xmm0 = ebx.hitpoint.spectrum
    macro eq128 Lr = xmm1
    macro eq128 Ld = xmm0
    macro dot xmm2 = xmm1 * xmm1
    macro eq32 transmitance = xmm2
    mov dword [cur_depth], 1

    macro eq128 xmm3 = one
    macro dot xmm3 = xmm3 * ebx.hitpoint.le 
    macro if xmm3 > epsilon goto emiter_hit

    _path_construct:
    mov eax, dword [cur_depth]
    cmp eax, dword [max_depth]
    je __end_path
    macro eq32 xmm0 = transmitance
    macro if xmm0 < epsilon goto __end_path
    mov eax, r1
    mov ebx, hp
    call scene_isect 
    cmp eax, 0
    je __end_path
    mov eax, hp
    mov ebx, r1
    macro eq128 eax.hitpoint.wo = ebx.ray.dir * minus_one 
    call shade
    mov ebx, hp
    macro eq128 xmm3 = one
    macro dot xmm3 = xmm3 * ebx.hitpoint.le 
    macro if xmm3 > epsilon goto __end_path_light
    mov eax, r1
    macro eq128 eax.ray.origin = ebx.hitpoint.hit 
    macro eq128 eax.ray.dir = ebx.hitpoint.wi
    macro eq32 xmm1 = ebx.hitpoint.ndotwi 
    macro eq32 xmm0 = ebx.hitpoint.pdf
    macro eq32 xmm1 = xmm1 / xmm0
    macro broadcast xmm1 = xmm1[0]
    macro eq128 xmm1 = xmm1 * ebx.hitpoint.brdf
    macro eq128 xmm0 = ebx.hitpoint.spectrum
    mov edx, dword [cur_depth]
    imul edx, edx, 16
    movaps oword [Lr + edx], xmm1
    movaps oword [Ld + edx], xmm0
    macro dot xmm2 = xmm1 * xmm1
    macro eq32 transmitance = xmm2
    add dword [cur_depth], 1

    jmp _path_construct

    __end_path_light:
    ;macro eq128 xmm0 = ebx.hitpoint.le
    macro eq128 xmm0 = zero
    jmp _end_p

    __end_path:
    macro eq128 xmm0 = zero 

    _end_p:
    mov edx, dword [cur_depth]
    sub edx, 1
    imul edx, edx, 16
    movaps xmm2, oword [Lr + edx]
    movaps xmm3, oword [Ld + edx]
    macro eq128 xmm0 = xmm0 * xmm2
    macro eq128 xmm0 = xmm0 + xmm3

    sub dword [cur_depth], 1
    jnz _end_p

    mov eax, hp
    macro eq128 eax.hitpoint.spectrum = xmm0
    mov ebx, sam 
    call add_sample
    mov dword [cur_depth], 0
    jmp _next_sample
    

    emiter_hit:
    macro eq128 ebx.hitpoint.spectrum = ebx.hitpoint.le
    mov eax, ebx
    mov ebx, sam
    call add_sample
    mov dword [cur_depth], 0
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

ren.prepare_for_rendering()
runtime = Runtime()
ren.get_sampler().get_sample_asm(runtime, "get_sample")
ren.get_camera().ray_asm(runtime, "generate_ray")

renmas.shapes.linear_isect_asm(runtime, "scene_isect", ren.dyn_arrays())
renmas.shapes.visible_asm(runtime, "visible", "scene_isect")
renmas.core.generate_shade(runtime, "shade", "visible")
ren.get_film().add_sample_asm(runtime, "add_sample")

asm = renmas.utils.get_asm()
mc = asm.assemble(ASM)
ds = runtime.load("path_tracer", mc)

def path_tracer(tile):
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()

    sample = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)

    runtime.run("path_tracer") #100% rendering in assembly language

duration = 0.0
image_saved = False
def render_scene():
    tile = next_tile()
    if tile is None: 
        global image_saved
        if not image_saved:
            film = ren.get_film()
            film.tone_map()
            blt_float_img_to_window(0, 0, film.image, win)
            save_image(film, "Image6.png")
            image_saved = True
        return
    start = time.clock()
    path_tracer(tile)
    end = time.clock()
    global duration
    duration = duration + (end - start)
    print(tile, duration)

    film = ren.get_film()
    blt_float_img_to_window(0, 0, film.image, win)

win = renmas.gui.MainWindow(600, 400, "Test")
win.redraw()
win.render_handler(render_scene)
winlib.MainLoop()



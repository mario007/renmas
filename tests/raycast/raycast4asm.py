
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

#dragon()
sphere()


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
ds = runtime.load("raycast", mc)

def raycast(tile):
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()

    sample = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)

    runtime.run("raycast") #100% rendering in assembly language

duration = 0.0
image_saved = False
def render_scene():
    tile = next_tile()
    if tile is None: 
        global image_saved
        if not image_saved:
            film = ren.get_film()
            save_image(film, "Image5.png")
            image_saved = True
        return
    start = time.clock()
    raycast(tile)
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


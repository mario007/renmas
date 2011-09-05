
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
#cornell_scene()
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

def path_tracer(tile):
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()

    shapes = ren.isect_shapes()
    isect = renmas.shapes.isect #intersection rutine
    shade = renmas.core.shade

    background = renmas.core.Spectrum(0.00, 0.00, 0.00) 
    hp2 = renmas.shapes.HitPoint()
    hp3 = renmas.shapes.HitPoint()
    hp2.spectrum = background

    sample = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)

    Lr = [] #reflection coefficient
    Ld = [] #direct light
    transmitance = 1.0
    cur_depth = 0
    max_depth = 4

    #current implementation stop tracing path when we hit emitter
    while True:
        sam = sampler.get_sample(sample)
        if sam is None: break 
        ray = camera.ray(sample)
        hp = isect(ray, shapes)

        if hp is None:
            film.add_sample(sample, hp2) #background
            continue 

        hp.wo = ray.dir * -1.0
        shade(hp)
        kr = hp.brdf * (1.0 / hp.pdf) * hp.ndotwi
        transmitance *= kr.r #FIXME take component that has maximum value
        Lr.append(kr)
        Ld.append(hp.spectrum)

        cur_depth = 1
        ray.dir = hp.wi #in wi is next direction
        ray.origin = hp.hit_point
        if hp.le.r > 0.01: #primiray ray hit emitter - stop path 
            hp.spectrum = hp.le
            film.add_sample(sample, hp) 
            Lr = [] 
            Ld = []
            transmitance = 1.0
            cur_depth = 0
            continue

        Le = renmas.core.Spectrum(0.00, 0.00, 0.00) 

        while True:
            if cur_depth == max_depth: break
            if transmitance < 0.0001: break
            hp = isect(ray, shapes)
            if hp is None: break
            hp.wo = ray.dir * -1.0
            shade(hp)
            if hp.le.r > 0.0001: 
                #Le = hp.le
                break #we hit emiter FIXME - we dont't have to stop think for better implementation !!!!
            kr = hp.brdf * (1.0 / hp.pdf) * hp.ndotwi
            Lr.append(kr)
            Ld.append(hp.spectrum)
            ray.dir = hp.wi #in wi is next direction
            ray.origin = hp.hit_point
            transmitance *= kr.r #FIXME take component that has maximum value 
            cur_depth += 1

        tmp_spec = Le
        for i in range(cur_depth):

            brdf = Lr.pop()
            ld = Ld.pop()
            tmp_spec = tmp_spec.mix_spectrum(brdf) + ld

        hp3.spectrum = tmp_spec 
        film.add_sample(sample, hp3) 
            
        Lr = [] 
        Ld = []
        transmitance = 1.0
        cur_depth = 0
        

ren.prepare_for_rendering()

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
            save_image(film, "Image5.png")
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



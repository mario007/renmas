
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

def raycast(tile):
    sampler = ren.get_sampler()
    camera = ren.get_camera()
    film = ren.get_film()

    shapes = ren.isect_shapes()
    isect = renmas.shapes.isect #intersection rutine
    shade = renmas.core.shade

    background = renmas.core.Spectrum(0.00, 0.00, 0.00) 
    hp2 = renmas.shapes.HitPoint()
    hp2.spectrum = background

    sample = renmas.samplers.Sample()
    x, y, width, height = tile
    sampler.tile(x, y, width, height)

    while True:
        sam = sampler.get_sample(sample)
        if sam is None: break 
        ray = camera.ray(sample)
        hp = isect(ray, shapes)

        if hp is None:
            film.add_sample(sample, hp2) #background
        else:
            hp.wo = ray.dir * -1.0
            shade(hp)
            film.add_sample(sample, hp) #background

ren.prepare_for_rendering()

duration = 0.0
def render_scene():
    tile = next_tile()
    if tile is None: return
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


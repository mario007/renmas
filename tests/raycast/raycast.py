
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

def build_scene():
    ren.create_sphere(0, 0, 0, 3)
    
    shapes = ren.lst_shapes()
    return shapes

film = renmas.core.Film(100, 100, 1)
#sampler = renmas.samplers.RegularSampler(100, 100)
sampler = renmas.samplers.RandomSampler(100, 100, n=1)
sample = renmas.samplers.Sample()
camera = ren.pinhole_camera((5,5,5), (0,0,0), 100)

shapes = build_scene()

isect = renmas.shapes.isect

background = renmas.core.Spectrum(0.05, 0.05, 0.05) 
mis = renmas.core.Spectrum(0.0, 0.99, 0.0) 
hp2 = renmas.shapes.HitPoint()
hp2.spectrum = background

#raycast algorithm
start = time.clock()

ntile = -1 
lst_tiles = [(0,0,50,50), (50,0, 50, 50), (0,50,50,50), (50,50,50,50)]

#col = renmas.core.Spectrum(0.3, 0.5, 0.8) 
col = renmas.core.Spectrum(0.5, 0.2, 0.5) 
black = renmas.core.Spectrum(0.0, 0.0, 0.0) 
pos = renmas.maths.Vector3(10.0, 5.0, 8.0)
plight = renmas.lights.PointLight(pos, col) 


mat1 = renmas.materials.Material()
lamb = renmas.materials.Lambertian(0.6)
mat1.add_component(lamb)

col6 = renmas.core.Spectrum(0.6, 0.6, 0.6)
phong = renmas.materials.Phong(col6, 4.5)
mat1.add_component(phong)

def next_tile():
    global ntile
    if ntile == 3:
        return None
    ntile += 1
    print (ntile)
    return lst_tiles[ntile]

def raycast():
    tile = next_tile()
    if tile is None: return None
    x, y, width, height = tile
    print(tile)
    sampler.tile(x, y, width, height)

    while True:
        sam = sampler.get_sample(sample)
        if sam is None: break
        ray = camera.ray(sample)
        hp = isect(ray, shapes, 999999.0)
        if hp is None:
            film.add_sample(sample, hp2) #background
        else:
            if plight.L(hp) is True: #light is visible
                hp.wo = ray.dir * -1.0
                mat1.brdf(hp)
                #hp.spectrum = hp.spectrum * hp.ndotwi
                film.add_sample(sample, hp)
            else:
                hp.spectrum = black 
                film.add_sample(sample, hp)

    blt_float_img_to_window(0, 0, blitter, film.image, win)
    return True

end = time.clock()

print("Renderiranje je trajalo", end - start)

def blt_float_img_to_window(x, y, blitter, img, win):
    da, dpitch = win.get_addr()
    dw, dh = win.get_size()
    sa, spitch = img.get_addr()
    sw, sh = img.get_size()
    blitter.blt_floatTorgba(da, x, y, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)

win = renmas.gui.MainWindow(500, 500, "Test")

blitter = renmas.gui.Blitter()
blt_float_img_to_window(0, 0, blitter, film.image, win)

win.redraw()
win.render_handler(raycast)
winlib.MainLoop()


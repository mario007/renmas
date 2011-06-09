
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

def create_materials():
    ren.create_lambertian("m1", 0.8, 0.6, 0.2)
    ren.create_phong("m2", 0.4, 0.2, 0.5, 6)
    ren.create_phong("m3", 0.1, 0.1, 0.4, 2)
    ren.create_oren("m4", 0.8, 0.6, 0.2, 5.1)
    ren.create_oren_phong("m5", 0.4, 0.3, 0.2, 2.1, 20)
    ren.create_oren_phong("m6", 0.1, 0.2, 0.4, 4.9, 5)

def build_scene():
    idx = ren.get_mat_idx("m1")
    ren.create_sphere(0, 0, 0, 5, idx)
    idx3 = ren.get_mat_idx("m4")
    ren.create_sphere(0, 10, 0, 5, idx3)
    idx3 = ren.get_mat_idx("m6")
    ren.create_sphere(0, 0, -10, 4, idx3)

    idx4 = ren.get_mat_idx("m5")
    ren.create_sphere(0, 0, 10, 4, idx4)

    idx5 = ren.get_mat_idx("m5")
    ren.create_triangle((8,5,5), (4, 9, 8), (5, -2, 3), idx5)

    shapes = ren.lst_shapes()
    return shapes

def create_lights():
    ren.create_point_light("p1", (10, 10, 9), (1.0, 1.0, 1.0))

create_materials()
shapes = build_scene()
create_lights()

WIDTH = 200
HEIGHT = 200 
NSAMPLES = 1 
film = renmas.core.Film(WIDTH, HEIGHT, NSAMPLES)
#sampler = renmas.samplers.RegularSampler(100, 100)
sampler = renmas.samplers.RandomSampler(WIDTH, HEIGHT, n=NSAMPLES)
sample = renmas.samplers.Sample()
camera = ren.pinhole_camera((14,5.0,0), (0,5.0,0), 250)

isect = renmas.shapes.isect

background = renmas.core.Spectrum(0.05, 0.05, 0.05) 
mis = renmas.core.Spectrum(0.0, 0.99, 0.0) 
hp2 = renmas.shapes.HitPoint()
hp2.spectrum = background

#raycast algorithm
start = time.clock()

ntile = -1 
#lst_tiles = [(0,0,50,50), (50,0, 50, 50), (0,50,50,50), (50,50,50,50)]

col = renmas.core.Spectrum(0.65, 0.45, 0.75) 
black = renmas.core.Spectrum(0.0, 0.0, 0.0) 
pos = renmas.maths.Vector3(10.0, 5.0, 8.0)
plight = renmas.lights.PointLight(pos, col) 


def list_tiles(width, height, nsamples):
    # TODO - implement later smarter version to include number os sample and assembly version
    w = 50
    h = 50 
    
    sx = 0
    sy = 0
    xcoords = []
    ycoords = []
    tiles = []
    while sx < width:
        xcoords.append(sx)
        sx += w
    last_w = width - (sx - w) 
    while sy < height:
        ycoords.append(sy)
        sy += h
    last_h = height - (sy - h)

    for i in xcoords:
        for j in ycoords:
            tw = w
            th = h
            if i == xcoords[-1]:
                tw = last_w
            if j == ycoords[-1]:
                th = last_h
            tiles.append((i, j, tw, th))

    #print(xcoords)
    #print(ycoords)
    #print(last_w, last_h)
    #print(tiles)
    return tiles

lst_tiles = list_tiles(WIDTH, HEIGHT, NSAMPLES) 
lst_lights = ren.lst_lights()    

def save_image(film):
    blitter = renmas.gui.Blitter()

    wid, he = film.image.get_size()
    img = renmas.gui.ImageRGBA(wid, he)


    dw, dh = img.get_size()
    da, dpitch = img.get_addr()
    sw, sh = film.image.get_size()
    sa, spitch = film.image.get_addr()
    blitter.blt_floatTorgba(da, 0, 0, dw, dh, dpitch, sa, 0, 0, sw, sh, spitch)
    renmas.gui.save_image("Image1.png", img)

def shade(sample, hp):
    #loop through lights
    tmp_spec = renmas.core.Spectrum(0.0, 0.0, 0.0)
    for light in lst_lights:
        if light.L(hp) is True: #light is visible
            #mat1.brdf(hp)
            ren.get_material(hp.material).brdf(hp)
            tmp_spec = tmp_spec + hp.spectrum
            #hp.spectrum = hp.spectrum * hp.ndotwi
        else:
            hp.spectrum = black 

    hp.spectrum = tmp_spec
    film.add_sample(sample, hp)

def next_tile():
    global ntile
    if ntile == len(lst_tiles) - 1:
        return None
    ntile += 1
    return lst_tiles[ntile]

def raycast():
    tile = next_tile()
    if tile is None: 
        save_image(film)
        return None
    x, y, width, height = tile
    sampler.tile(x, y, width, height)

    while True:
        sam = sampler.get_sample(sample)
        if sam is None: break
        ray = camera.ray(sample)
        hp = isect(ray, shapes, 999999.0)
        if hp is None:
            film.add_sample(sample, hp2) #background
        else:
            hp.wo = ray.dir * -1.0
            shade(sample, hp)

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


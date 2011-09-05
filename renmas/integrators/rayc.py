
import renmas
import renmas.interface as ren 

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

def raycast_integrator(tile, renderer):
    sampler = renderer._sampler
    camera = renderer._camera
    film = renderer._film

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
        hp = renderer._isect(ray)

        if hp is None or hp is False:
            film.add_sample(sample, hp2) #background
        else:
            hp.wo = ray.dir * -1.0
            renderer._shade(hp)
            film.add_sample(sample, hp) #background


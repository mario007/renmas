
import renmas

def path_integrator(tile, renderer):
    sampler = renderer._sampler
    camera = renderer._camera
    film = renderer._film

    background = renmas.core.Spectrum(0.99, 0.99, 0.99) 
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
        hp = renderer._isect(ray)

        if hp is None or hp is False:
            film.add_sample(sample, hp2) #background
            continue 

        hp.wo = ray.dir * -1.0
        renderer._shade(hp)
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
            hp = renderer._isect(ray)
            if hp is None or hp is False: break
            hp.wo = ray.dir * -1.0
            renderer._shade(hp)
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
        

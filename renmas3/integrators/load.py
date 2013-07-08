

_integrators = {}

def get_integrator_code(name):
    if name in _integrators:
        return _integrators[name]
    return None

Simple_2D = """
sample = Sample()
ray = Ray()
hitpoint = Hitpoint()
shadepoint = Shadepoint()
background = (0.0, 0.0, 0.0)

ret = 1
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    if ret == 0:
        break
    hit = isect(ray, hitpoint)
    if hit:
        bsdf(hitpoint, shadepoint, hitpoint.material_idx)
        col = spectrum_to_rgb(shadepoint.material_reflectance)
        add_sample(sample, col)
    else:
        add_sample(sample, background)
"""

_integrators['simple2D'] = Simple_2D

Raycast_code = """
sample = Sample()
ray = Ray()
hitpoint = Hitpoint()
shadepoint = Shadepoint()
background = (0.1, 0.5, 0.1)
background = (0.0, 0.0, 0.0)

nlights = number_of_lights()
ret = 1
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    if ret == 0:
        break
    hit = isect(ray, hitpoint)
    if hit:
        shadepoint.wo = ray.dir * -1.0
        ndotwo = dot(hitpoint.normal, shadepoint.wo)

        idx = 0
        acum_col = spectrum(0.0)
        emission(hitpoint, shadepoint, hitpoint.material_idx)
        acum_col = acum_col + shadepoint.material_emission
        while idx < nlights:
            if ndotwo > 0.0:
                light_radiance(hitpoint, shadepoint, idx)
                ndotwi = dot(hitpoint.normal, shadepoint.wi)
                if ndotwi > 0.0:
                    vis = visible(hitpoint.hit, shadepoint.light_position)
                    if vis:
                        bsdf(hitpoint, shadepoint, hitpoint.material_idx)
                        col = ndotwi * shadepoint.material_reflectance * shadepoint.light_intensity
                        acum_col = acum_col + col
            idx = idx + 1

        v = spectrum_to_rgb(acum_col)
        add_sample(sample, v)
    else:
        add_sample(sample, background)
"""

_integrators['raycast'] = Raycast_code

Pathtracer_code = """
sample = Sample()
ray = Ray()
hitpoint = Hitpoint()
shadepoint = Shadepoint()
background = (0.1, 0.5, 0.1)
#background = (0.0, 0.0, 0.0)

nlights = number_of_lights()
max_depth = 10
treshold = 0.01 

ret = 1
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    if ret == 0:
        break
    hit = isect(ray, hitpoint)
    if hit:
        cur_depth = 1
        acum_col = spectrum(0.0)
        path = spectrum(1.0)

        cont = 1
        while cont:

            shadepoint.wo = ray.dir * -1.0
            ndotwo = dot(hitpoint.normal, shadepoint.wo)

            emission(hitpoint, shadepoint, hitpoint.material_idx)
            mat_em = shadepoint.material_emission
            lum_em = luminance(mat_em)
            if lum_em > 0.001: # we directly hit light
                mat_em = mat_em * path
                acum_col = acum_col + mat_em
                #if cur_depth == 1:
                #    acum_col = acum_col + mat_em
                break

            #direct lighting
            idx = 0
            while idx < nlights:
                if ndotwo > 0.0:
                    light_radiance(hitpoint, shadepoint, idx)
                    ndotwi = dot(hitpoint.normal, shadepoint.wi)
                    if ndotwi > 0.0:
                        vis = visible(hitpoint.hit, shadepoint.light_position)
                        if vis:
                            bsdf(hitpoint, shadepoint, hitpoint.material_idx)
                            col = ndotwi * shadepoint.material_reflectance * shadepoint.light_intensity
                            col = col * path
                            acum_col = acum_col + col
                idx = idx + 1

            if cur_depth > max_depth: 
                break
            path_lum = luminance(path)
            if path_lum < treshold:
                break
            
            sample_bsdf(hitpoint, shadepoint, hitpoint.material_idx)
            bsdf(hitpoint, shadepoint, hitpoint.material_idx)
            pdf_bsdf(hitpoint, shadepoint, hitpoint.material_idx)
            ndotwi = dot(hitpoint.normal, shadepoint.wi)
            if ndotwi < 0.0:
                ndotwi = ndotwi * -1.0
            pdf = ndotwi / shadepoint.pdf
            path = path * shadepoint.material_reflectance * pdf

            ray.origin = hitpoint.hit
            ray.dir = shadepoint.wi
            hit2 = isect(ray, hitpoint)
            if hit2 == 0:
                break
            cur_depth = cur_depth + 1

        v = spectrum_to_rgb(acum_col)
        add_sample(sample, v)
    else:
        add_sample(sample, background)
"""

_integrators['pathtracer'] = Pathtracer_code

def render_py(self, tile):
    ren = self._renderer
    sampler = ren.sampler
    sampler.set_tile(tile)
    camera = ren.camera
    intersector = ren.intersector
    film = ren.film
    shader = ren.shader
    conv = ren.converter

    background = ren.converter.create_spectrum((0.00, 0.0, 0.0))

    path = background.zero_spectrum()
    path.set(1.0)
    max_depth = 9 
    treshold = 0.01 
    counter = 0

    while True:
        sam = sampler.get_sample()
        if sam is None: break 
        ray = camera.ray(sam) 
        hp = intersector.isect(ray) 
        if hp:
            L = background.zero_spectrum()
            path = background.zero_spectrum()
            path.set(1.0)
            cur_depth = 1
            while True:
                hp.wo = ray.dir * -1.0
                hp.fliped = False
                if hp.normal.dot(ray.dir) > 0.0:
                    hp.normal = hp.normal * -1.0
                    hp.fliped = True
                hp.specular = 0
                spectrum = shader.shade(hp)

                L = L + spectrum.mix_spectrum(path)
                Y = conv.Y(path)
                #print(cur_depth, Y)
                if cur_depth >= max_depth or Y < treshold: 
                    film.add_sample(sam, L)
                    break
                material = shader._materials_idx[hp.material]
                hp.specular = 0

                #material.next_direction(hp)
                material.next_direction_bsdf(hp)
                #material.f(hp)

                path = path.mix_spectrum(hp.f_spectrum*(1.0/hp.pdf))
                cur_depth += 1
                
                ray = Ray(hp.hit_point, hp.wi)
                hp = intersector.isect(ray) 
                if not hp: 
                    if shader.environment_light is not None:
                        le = shader.environment_light.Le(ray.dir)
                        L = L + le.mix_spectrum(path)
                        film.add_sample(sam, L)
                    else:
                        film.add_sample(sam, L)
                    break
                
            #film.add_sample(sam, L)
        else:
            if shader.environment_light is not None:
                film.add_sample(sam, shader.environment_light.Le(ray.dir))
            else:
                film.add_sample(sam, background)

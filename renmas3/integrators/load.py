

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
        col = spectrum_to_rgb(shadepoint.material_spectrum)
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

nlights = number_of_lights()
ret = 1
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(sample, ray)
    if ret == 0:
        break
    hit = isect(ray, hitpoint)
    if hit:
        idx = 0
        acum_col = spectrum(0.0)
        while idx < nlights:
            shadepoint.wo = ray.dir * -1.0
            ndotwo = dot(hitpoint.normal, shadepoint.wo)
            if ndotwo > 0.0:
                light_radiance(hitpoint, shadepoint, idx)
                ndotwi = dot(hitpoint.normal, shadepoint.wi)
                if ndotwi > 0.0:
                    vis = visible(hitpoint.hit, shadepoint.light_position)
                    if vis:
                        bsdf(hitpoint, shadepoint, hitpoint.material_idx)
                        col = ndotwi * shadepoint.material_spectrum * shadepoint.light_intensity
                        acum_col = acum_col + col
            idx = idx + 1

        v = spectrum_to_rgb(acum_col)
        add_sample(sample, v)
    else:
        add_sample(sample, background)
"""

_integrators['raycast'] = Raycast_code


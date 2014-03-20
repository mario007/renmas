

sample = Sample()
ray = Ray()
hitpoint = HitPoint()
shadepoint = ShadePoint()

background_color = (0.0, 0.0, 0.0, 0.99)

nlights = number_of_lights()

while 1:
    ret = generate_sample(sample)
    if ret == 0:
        break

    generate_ray(ray, sample)
    min_dist = 99999.0
    hit = isect_scene(ray, hitpoint, min_dist)

    if hit:
        acum_col = Spectrum(0.0)
        shadepoint.wo = ray.direction * -1.0

        ndotwo = dot(hitpoint.normal, shadepoint.wo)
        idx = 0
        while idx < nlights:
            if ndotwo > 0.0:
                light_radiance(hitpoint, shadepoint, idx)
                ndotwi = dot(hitpoint.normal, shadepoint.wi)
                if ndotwi > 0.0:
                    vis = visibility(hitpoint.hit, shadepoint.light_position)
                    if vis:
                        material_reflectance(hitpoint, shadepoint, hitpoint.mat_idx)
                        col = ndotwi * shadepoint.material_reflectance * shadepoint.light_intensity
                        acum_col = acum_col + col
            idx = idx + 1

        c = spectrum_to_vec(acum_col)
        color = float4(c[0], c[1], c[2], 0.99)
    else:
        color = background_color

    rgba = get_rgba(hdr_buffer, sample.ix, sample.iy)

    flt_weight = 0.99 # TODO filters box filter
    color = color * flt_weight + rgba * rgba[3]

    acum_weight = rgba[3] + flt_weight
    color = color * (1.0 / acum_weight)
    color = float4(color[0], color[1], color[2], acum_weight)

    set_rgba(hdr_buffer, sample.ix, sample.iy, color)



sample = Sample()
ray = Ray()
hitpoint = HitPoint()
shadepoint = ShadePoint()

nlights = number_of_lights()

while 1:
    ret = generate_sample(sample)
    if ret == 0:
        break

    generate_ray(ray, sample)
    min_dist = 99999.0
    hit = isect_scene(ray, hitpoint, min_dist)
    shadepoint.wo = ray.direction * -1.0

    if hit:
        acum_col = Spectrum(0.0)

        if hitpoint.light_id >= 0:  # we directly hit light
            light_emission(hitpoint, shadepoint, hitpoint.light_id)
            acum_col = acum_col + shadepoint.material_emission
        else:
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
                            col = shadepoint.material_reflectance * shadepoint.light_intensity * (ndotwi / shadepoint.light_pdf)
                            acum_col = acum_col + col
                idx = idx + 1

        c = spectrum_to_vec(acum_col)
        color = float4(c[0], c[1], c[2], 0.99)
    else:
        environment_emission(hitpoint, shadepoint)
        c = spectrum_to_vec(shadepoint.light_intensity)
        color = float4(c[0], c[1], c[2], 0.99)

    rgba = get_rgba(hdr_buffer, sample.ix, sample.iy)

    flt_weight = 0.99 # TODO filters box filter
    color = color * flt_weight + rgba * rgba[3]

    acum_weight = rgba[3] + flt_weight
    color = color * (1.0 / acum_weight)
    color = float4(color[0], color[1], color[2], acum_weight)

    set_rgba(hdr_buffer, sample.ix, sample.iy, color)

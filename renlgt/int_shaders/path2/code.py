

sample = Sample()
ray = Ray()
hitpoint = HitPoint()
shadepoint = ShadePoint()

nlights = number_of_lights()
max_depth = 10
treshold = 0.01 
min_dist = 99999.0

while 1:
    ret = generate_sample(sample)
    if ret == 0:
        break

    generate_ray(ray, sample)

    cur_depth = 1
    acum_col = Spectrum(0.0)
    path_weight = Spectrum(1.0)
    last_pdf = 1.0

    while 1:

        hit = isect_scene(ray, hitpoint, min_dist)
        shadepoint.wo = ray.direction * -1.0

        # ray misis whole scene
        if hit == 0:
            environment_emission(hitpoint, shadepoint)
            acum_col = acum_col + shadepoint.light_intensity * path_weight
            break

        # direct hit of light
        if hitpoint.light_id >= 0:
            # we cheat here, we inlucde only first light hit to reduce noise
            #if cur_depth == 1:
            light_emission(hitpoint, shadepoint, hitpoint.light_id)
            acum_col = acum_col + shadepoint.material_emission * path_weight
            break #light do not reflect

        #explicit direct lighting
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
                        acum_col = acum_col + col * path_weight
            idx = idx + 1

        if cur_depth > max_depth: 
            break
        path_lum = luminance(path_weight)
        if path_lum < treshold:
            break

        material_sampling(hitpoint, shadepoint, hitpoint.mat_idx)
        ndotwi = dot(hitpoint.normal, shadepoint.wi)
        if ndotwi < 0.0:
            ndotwi = ndotwi * -1.0
        # if shadepoint.pdf < 0.000001:
        #     break
        pdf = ndotwi / shadepoint.pdf
        if pdf < 0.000001:
            break
        path_weight = path_weight * shadepoint.material_reflectance * pdf

        ray.origin = hitpoint.hit
        ray.direction = shadepoint.wi
        cur_depth = cur_depth + 1
        
    c = spectrum_to_vec(acum_col)
    color = float4(c[0], c[1], c[2], 0.99)

    rgba = get_rgba(hdr_buffer, sample.ix, sample.iy)

    flt_weight = 0.99 # TODO filters box filter
    color = color * flt_weight + rgba * rgba[3]

    acum_weight = rgba[3] + flt_weight
    color = color * (1.0 / acum_weight)
    color = float4(color[0], color[1], color[2], acum_weight)

    set_rgba(hdr_buffer, sample.ix, sample.iy, color)

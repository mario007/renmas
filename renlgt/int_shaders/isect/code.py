

sample = Sample()
ray = Ray()
hitpoint = HitPoint()

hit_color = (0.9, 0.9, 0.9, 0.99)
miss_color = (0.0, 0.0, 0.0, 0.99)

ret = 1
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(ray, sample)
    min_dist = 99999.0
    hit = isect_scene(ray, hitpoint, min_dist)

    #we support multiple samples per pixel(antialiasing)
    x = sample.ix
    y = sample.iy

    rgba = get_rgba(hdr_buffer, x, y)
    acum_weight = rgba[3]
    rgba = rgba * acum_weight

    flt_weight = 0.99 # TODO filters box filter
    if hit:
        new_color = hit_color * flt_weight
    else:
        new_color = miss_color * flt_weight

    new_col = new_color + rgba

    acum_weight = acum_weight + flt_weight

    new_col = new_col * (1.0 / acum_weight)
    new_col = float4(new_col[0], new_col[1], new_col[2], acum_weight)

    set_rgba(hdr_buffer, x, y, new_col)

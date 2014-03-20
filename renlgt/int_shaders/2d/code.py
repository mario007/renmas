
sample = Sample()
ray = Ray()
hitpoint = HitPoint()
shadepoint = ShadePoint()

background_color = (0.0, 0.0, 0.0, 0.99)

while 1:
    ret = generate_sample(sample)
    if ret == 0:
        break

    generate_ray(ray, sample)
    min_dist = 99999.0
    hit = isect_scene(ray, hitpoint, min_dist)

    if hit:
        material_reflectance(hitpoint, shadepoint, hitpoint.mat_idx)
        color = spectrum_to_vec(shadepoint.material_reflectance)
        color = float4(color[0], color[1], color[2], 0.99)
    else:
        color = background_color

    rgba = get_rgba(hdr_buffer, sample.ix, sample.iy)

    flt_weight = 0.99 # TODO filters box filter
    color = color * flt_weight + rgba * rgba[3]

    acum_weight = rgba[3] + flt_weight
    color = color * (1.0 / acum_weight)
    color = float4(color[0], color[1], color[2], acum_weight)

    set_rgba(hdr_buffer, sample.ix, sample.iy, color)

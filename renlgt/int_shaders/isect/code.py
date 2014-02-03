

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
    if hit:
        set_rgba(hdr_buffer, sample.ix, sample.iy, hit_color)
    else:
        set_rgba(hdr_buffer, sample.ix, sample.iy, miss_color)
    #rgba = get_rgba(hdr_buffer, 0, 0)
    #set_rgba(hdr_buffer, sample.ix, sample.iy, val)


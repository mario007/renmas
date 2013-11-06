

ray = Ray()
sample = Sample()
hitpoint = HitPoint()

min_dist = 99999.0

ret = 1
while ret != 0:
    ret = generate_sample(sample)
    generate_ray(ray, sample)
    hit = isect_scene(ray, hitpoint, min_dist)
    if hit:
        set_rgba(image, sample.ix, sample.iy, hit_color)
    else:
        set_rgba(image, sample.ix, sample.iy, background)


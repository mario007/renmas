
sample = sample_hemisphere()
w = hitpoint.normal 
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)
ndir = u * sample[0] + v * sample[1] + w * sample[2]
shadepoint.wi = normalize(ndir)


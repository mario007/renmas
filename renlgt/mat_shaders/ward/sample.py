
tmp = random()
if tmp < 0.5:
    # Sampling of diffuse ray
    r1 = random()
    r2 = random()
    e = 1.0

    phi = 2.0 * 3.14159 * r1
    exponent = 1.0 / (e + 1.0)
    cos_theta = pow(r2, exponent)

    tmp = 1.0 - cos_theta * cos_theta
    sin_theta = sqrt(tmp)
    sin_phi = sin(phi)
    cos_phi = cos(phi)
    pu = sin_theta * cos_phi 
    pv = sin_theta * sin_phi
    pw = cos_theta

    w = hitpoint.normal 
    tv = (0.0034, 1.0, 0.0071)
    v = cross(tv, w)
    v = normalize(v)
    u = cross(v, w)

    ndir = u * pu + v * pv + w * pw
    shadepoint.wi = normalize(ndir)

    __material_pdf(hitpoint, shadepoint, ptr_mat_pdf)
    __material_reflectance(hitpoint, shadepoint, ptr_mat_bsdf)
    return 0

# Sampling of specular ray
u = random()
v = random()

angle = 2.0 * 3.14159 * v
x = beta * sin(angle)
y = 1.0 / (alpha * cos(angle))
phi = atanr2(x, y)

cos_phi = cos(phi)
sin_phi = sin(phi)

t1 = (cos_phi * cos_phi) / (alpha * alpha)
t2 = (sin_phi * sin_phi) / (beta * beta)
tmp = (log(u) * -1.0) / (t1 + t2)
tmp = sqrt(tmp)

theta = atan(tmp)

sin_theta = sin(theta)
cos_theta = cos(theta)
x = sin_theta * cos_phi
y = sin_theta * sin_phi

h = float3(x, y, cos_theta)
h = normalize(h)

wi = 2.0 * dot(shadepoint.wo, h) * h - shadepoint.wo

shadepoint.wi = normalize(wi)

__material_pdf(hitpoint, shadepoint, ptr_mat_pdf)
__material_reflectance(hitpoint, shadepoint, ptr_mat_bsdf)

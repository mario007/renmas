
r1 = random()
r2 = random()

tmp = random()
if tmp > 0.5: # diffuse direction
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

# specular direction
u1 = r1
if r1 > 0.25: #second quadrant
    if r1 < 0.5:
        u1 = 4.0 * (0.5 - r1)

if r1 > 0.5: # third quadrant
    if r1 < 0.75:
        u1 = 4.0 * (r1 - 0.5) 

if r1 > 0.75: # fourth quadrant
    u1 = 4.0 * (1.0 - r1)

tmp = u1 * 3.14159 * 0.5
tmp2 = (nu + 1.0) / (nv + 1.0)
tmp = sqrt(tmp2) * tan(tmp)
phi = atan(tmp)

cos_phi = cos(phi)
sin_phi = sin(phi)
exponent = 1.0 / (nu * cos_phi * cos_phi + nv * sin_phi * sin_phi + 1.0)
cos_theta = pow(r2, exponent)

if r1 > 0.25: # scond quadrant
    if r1 < 0.5:
        phi = 3.14159 - phi

if r1 > 0.5: # third quadrant
    if r1 < 0.75:
        phi = 3.14159 + phi

if r1 > 0.75: # fourth quadrant
    phi = 2.0 * 3.14159 - phi

cos_phi = cos(phi)
sin_phi = sin(phi)

tmp = 1.0 - cos_theta * cos_theta
tmp = max(0.0, tmp)
sin_theta = sqrt(tmp)

x = sin_theta * cos_phi
y = sin_theta * sin_phi
h = float3(x, y, cos_theta)
h = normalize(h)

wi = 2.0 * dot(shadepoint.wo, h) * h - shadepoint.wo
wi = normalize(wi)
ndotwi = dot(hitpoint.normal, wi)
if ndotwi < 0.0: #sampling direction is below surface
    wi = wi * -1.0
shadepoint.wi = wi

__material_pdf(hitpoint, shadepoint, ptr_mat_pdf)
__material_reflectance(hitpoint, shadepoint, ptr_mat_bsdf)



r1 = random()
r2 = random()

davg = luminance(diffuse)
savg = luminance(specular)
weight = savg / (davg + savg)

tmp = random()
if tmp > weight: # diffuse direction
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
phi = 6.283185 * r2 # 2*math.pi = 6.28...

n1 = 2.0 / (exponent + 1.0)
n2 = 1.0 / (exponent + 1.0)

tmp1 = 1.0 - pow(r1, n1)
pu = sqrt(tmp1) * cos(phi)
pv = sqrt(tmp1) * sin(phi)
pw = pow(r1, n2)

ndotwo = dot(hitpoint.normal, shadepoint.wo)
r = hitpoint.normal * ndotwo * 2.0 - shadepoint.wo

w = r
tv = (0.0034, 1.0, 0.0071)
u = cross(tv, w)
u = normalize(u)
v = cross(u, w)

ndir = u * pu + v * pv + w * pw
ndir = normalize(ndir)
ndotndir = dot(hitpoint.normal, ndir)

if ndotndir < 0.0: #sampling direction is below surface
    pu = -1.0 * pu
    pv = -1.0 * pv
    ndir = u * pu + v * pv + w * pw
    ndir = normalize(ndir)

shadepoint.wi = ndir
__material_pdf(hitpoint, shadepoint, ptr_mat_pdf)
__material_reflectance(hitpoint, shadepoint, ptr_mat_bsdf)



tmp = random()

if tmp > 0.5: # diffuse direction
    sample = sample_hemisphere()
    w = hitpoint.normal 
    tv = (0.0034, 1.0, 0.0071)
    v = cross(tv, w)
    v = normalize(v)
    u = cross(v, w)
    ndir = u * sample[0] + v * sample[1] + w * sample[2]
    shadepoint.wi = normalize(ndir)
    return 0

# specular direction
r1 = random()
r2 = random()
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

if ndotndir < 0.0:
    pu = -1.0 * pu
    pv = -1.0 * pv
    ndir = u * pu + v * pv + w * pw
    ndir = normalize(ndir)

shadepoint.wi = ndir


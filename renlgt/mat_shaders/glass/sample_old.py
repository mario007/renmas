

ndotwo = dot(hitpoint.normal, shadepoint.wo)
eta = ior
eta = 1.5
normal = hitpoint.normal
if ndotwo < 0.0: # iniside surface is hit
    eta = 1.0 / eta
    normal = normal * -1.0
    ndotwo = ndotwo * -1.0
tmp = 1.0 - ndotwo * ndotwo
eta2 = eta * eta
tir = 1.0 - tmp / eta2

if tir < 0.0: #TIR happend -- we just sample reflection ray
    shadepoint.wi = normal * ndotwo * 2.0 - shadepoint.wo
    shadepoint.pdf = 1.0
    ndotwi = dot(hitpoint.normal, shadepoint.wi)
    if ndotwi < 0.0:
        ndotwi = ndotwi * -1.0
    reflectance = (1.0 / ndotwi) * Spectrum(1.0)
    shadepoint.material_reflectance = reflectance
    shadepoint.specular_bounce = 1
    return 0

tmp = ior - 1.0
tmp2 = ior + 1.0
R0 = tmp / tmp2
R0 = R0 * R0
wo = shadepoint.wo * -1.0
cosine = dot(wo, hitpoint.normal)
if cosine < 0.0:
    cosine = cosine * -1.0
tmp = 1.0 - cosine
tmp = tmp * tmp * tmp * tmp * tmp
tmp2 = 1.0 - R0
R = tmp * tmp2 + R0
k = 0.5
P = (1.0 - k) * R + 0.5 * k

tmp = random()
if tmp < P: # reflection ray
    shadepoint.wi = normal * ndotwo * 2.0 - shadepoint.wo
    ndotwi = dot(hitpoint.normal, shadepoint.wi)
    if ndotwi < 0.0:
        ndotwi = ndotwi * -1.0
    reflectance = (R / ndotwi) * Spectrum(1.0)
    shadepoint.material_reflectance = reflectance
    shadepoint.pdf = P 
    shadepoint.specular_bounce = 1
    return 0

theta2 = sqrt(tir)
tmp = theta2 - ndotwo / eta
tmp = tmp * normal
wo = shadepoint.wo * -1.0
tmp2 = 1.0 / eta
wt = wo * tmp2 - tmp
shadepoint.wi = normalize(wt)

ndotwi = dot(hitpoint.normal, shadepoint.wi)
if ndotwi < 0.0:
    ndotwi = ndotwi * -1.0

RT = 1.0 - R
eta = eta * eta
tmp = RT * eta / ndotwi
reflectance = tmp * Spectrum(1.0) 
shadepoint.material_reflectance = reflectance
shadepoint.pdf = 1.0 - P 
shadepoint.specular_bounce = 1




ndotwo = dot(hitpoint.normal, shadepoint.wo)
eta = ior
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
    shadepoint.reflection_type = 69
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
P = 0.5 * R + 0.25

tmp = random()
if tmp < P: # reflection ray
    shadepoint.wi = normal * ndotwo * 2.0 - shadepoint.wo
    shadepoint.reflection_type = 69
    return 0

theta2 = sqrt(tir)
tmp = theta2 - ndotwo / eta
tmp = tmp * normal
wo = shadepoint.wo * -1.0
tmp2 = 1.0 / eta
wt = wo * tmp2 - tmp
shadepoint.wi = normalize(wt)
shadepoint.reflection_type = 88 


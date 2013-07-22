

ndotwo = dot(hitpoint.normal, shadepoint.wo)
eta = ior
if ndotwo < 0.0: # iniside surface is hit
    eta = 1.0 / eta
tmp = 1.0 - ndotwo * ndotwo
eta2 = eta * eta
tir = 1.0 - tmp / eta2
if tir < 0.0: #TIR happend
    shadepoint.pdf = 1.0
    shadepoint.reflection_type = 0
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

#TODO improve this
if shadepoint.reflection_type == 69:
    shadepoint.pdf = P 
    shadepoint.reflection_type = 0
    return 0

if shadepoint.reflection_type == 88:
    shadepoint.pdf = 1.0 - P 
    shadepoint.reflection_type = 0
    return 0


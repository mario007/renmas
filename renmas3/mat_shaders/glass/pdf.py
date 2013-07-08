

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

#TODO improve this
if shadepoint.reflection_type == 69:
    shadepoint.pdf = 0.5
    shadepoint.reflection_type = 0
    return 0

if shadepoint.reflection_type == 88:
    shadepoint.pdf = 0.5
    shadepoint.reflection_type = 0
    return 0


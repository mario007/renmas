#hitpoint is argument to shader
#shadepoint is argument to shader

tmp = ior - 1.0
tmp2 = ior + 1.0
R0 = tmp / tmp2
R0 = R0 * R0

eta = ior
ndotwo = dot(hitpoint.normal, shadepoint.wo)
normal = hitpoint.normal
if ndotwo < 0.0:
    normal = normal * -1.0
    eta = 1.0 / eta

#TIR
tmp = 1.0 - ndotwo * ndotwo
eta2 = eta * eta
tir = 1.0 - tmp / eta2

# schlick aproximation of fresnel
wo = shadepoint.wo * -1.0
cosine = dot(wo, hitpoint.normal)
if cosine < 0.0:
    cosine = cosine * -1.0

tmp = 1.0 - cosine
tmp = tmp * tmp * tmp * tmp * tmp
tmp2 = 1.0 - R0
R = tmp * tmp2 + R0
if tir < 0.0:
    R = 1.0

ndotwi = dot(hitpoint.normal, shadepoint.wi)
if ndotwi < 0.0:
    ndotwi = ndotwi * -1.0

##BRDF - perfect specular direction
if shadepoint.reflection_type == 69:
    reflectance = R / ndotwi
    reflectance = reflectance * spectrum(1.0) 
    shadepoint.material_reflectance = reflectance 
    return 0

#BTDF - perfect transmission direction
if shadepoint.reflection_type == 88:
    RT = 1.0 - R
    eta = eta * eta
    tmp = RT * eta / ndotwi
    reflectance = tmp * spectrum(1.0) 
    shadepoint.material_reflectance = reflectance
    return 0

shadepoint.material_reflectance = spectrum(0.0)


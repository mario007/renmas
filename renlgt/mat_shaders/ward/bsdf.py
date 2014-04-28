#hitpoint is argument to shader
#shadepoint is argument to shader
# diffuse is property of shader

h = shadepoint.wo + shadepoint.wi
h = normalize(h)

ndotwo = dot(shadepoint.wo, hitpoint.normal)
if ndotwo < 0.0:
    shadepoint.material_reflectance = diffuse * 0.318309886
    return 0

ndotwi = dot(shadepoint.wi, hitpoint.normal)
if ndotwi < 0.0:
    shadepoint.material_reflectance = diffuse * 0.318309886
    return 0

tmp = ndotwo * ndotwi
denom = 4.0 * 3.14159 * alpha * beta * sqrt(tmp)

w = hitpoint.normal
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)

hxa = dot(h, u) / alpha
hyb = dot(h, v) / beta
hdotn = dot(h, w)

exponent = ((hxa * hxa + hyb * hyb) / (hdotn * hdotn)) * -1.0
spec_ref = specular * (exp(exponent) / denom)
shadepoint.material_reflectance = diffuse * 0.318309886 + spec_ref

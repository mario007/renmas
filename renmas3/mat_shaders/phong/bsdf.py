#hitpoint is argument to shader
#shadepoint is argument to shader
# diffuse is property of shader

ndotwi = dot(hitpoint.normal, shadepoint.wi)
r = hitpoint.normal * ndotwi * 2.0 - shadepoint.wi
rdotwo = dot(r, shadepoint.wo)
if rdotwo > 0.0:
    tmp = (exponent + 2.0) * 0.159154943 # 0.159... = 1 / (2 * math.pi)
    tmp = tmp * pow(rdotwo, exponent)
    tmp = tmp * specular
    shadepoint.material_reflectance = diffuse * 0.318309886 + tmp
    return 0

shadepoint.material_reflectance = diffuse * 0.318309886


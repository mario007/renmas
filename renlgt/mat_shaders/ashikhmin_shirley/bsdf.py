#hitpoint is argument to shader
#shadepoint is argument to shader
# diffuse is property of shader
# specular is property of shader
# nu, nv is property of shader


h = shadepoint.wo + shadepoint.wi
h = normalize(h)

w = hitpoint.normal
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)
ndotwi = dot(hitpoint.normal, shadepoint.wi)
ndotwo = dot(hitpoint.normal, shadepoint.wo)
hdotwo = dot(h, shadepoint.wo)

hdotu = dot(h, u)
hdotv = dot(h, v)
hdotn = dot(h, hitpoint.normal)

exponent = (nu * hdotu * hdotu + nv * hdotv * hdotv) / (1.0 - hdotn * hdotn)
tmp = (nu + 1.0) * (nv + 1.0)
const = sqrt(tmp) / (8.0 * 3.14159)
denom = hdotwo * max(ndotwi, ndotwo) 
tmp = 1.0 - hdotwo
tmp = tmp * tmp * tmp * tmp * tmp
fresnel = specular + (Spectrum(1.0) - specular) * tmp
spec_ref = (const * pow(hdotn, exponent) / denom) * fresnel

tmp = 1.0 - ndotwi * 0.5
tmp = tmp * tmp * tmp * tmp * tmp
tmp2 = 1.0 - ndotwo * 0.5
tmp2 = tmp2 * tmp2 * tmp2 * tmp2 * tmp2
tmp = (28.0 / (23.0 * 3.14159)) * (1.0 - tmp) * (1.0 - tmp2)
dif_ref = diffuse * (Spectrum(1.0) - specular) * tmp
shadepoint.material_reflectance = dif_ref + spec_ref


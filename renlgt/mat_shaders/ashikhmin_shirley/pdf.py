

h = shadepoint.wo + shadepoint.wi
h = normalize(h)

w = hitpoint.normal
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)

hdotu = dot(h, u)
hdotv = dot(h, v)
hdotn = dot(h, w)

tmp = (nu + 1.0) * (nv + 1.0)
const = sqrt(tmp) / (2.0 * 3.14159)

exponent = (nu * hdotu * hdotu + nv * hdotv * hdotv) / (1.0 - (hdotn * hdotn))
hdotwi = dot(h, shadepoint.wi)
pdf = (const * pow(hdotn, exponent)) / (4.0 * hdotwi)
#pdf = min(0.99, pdf)

ndotwi = dot(hitpoint.normal, shadepoint.wi)
shadepoint.pdf = (ndotwi * 0.318309886 + pdf) * 0.5


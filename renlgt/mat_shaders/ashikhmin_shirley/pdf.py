

# h = shadepoint.wo + shadepoint.wi
# h = normalize(h)

# w = hitpoint.normal
# tv = (0.0034, 1.0, 0.0071)
# v = cross(tv, w)
# v = normalize(v)
# u = cross(v, w)

# hdotu = dot(h, u)
# hdotv = dot(h, v)
# hdotn = dot(h, w)

# tmp = (nu + 1.0) * (nv + 1.0)
# const = sqrt(tmp) / (2.0 * 3.14159)

# exponent = (nu * hdotu * hdotu + nv * hdotv * hdotv) / (1.0 - (hdotn * hdotn))
# hdotwi = dot(h, shadepoint.wi)
# pdf = (const * pow(hdotn, exponent)) / (4.0 * hdotwi)
# #pdf = min(3.8, pdf)

# #pdf = (4.0 * hdotwi) / (const * pow(hdotn, exponent))

# ndotwi = dot(hitpoint.normal, shadepoint.wi)
# shadepoint.pdf = (ndotwi * 0.318309886 + pdf) * 0.5

h = shadepoint.wo + shadepoint.wi
h = normalize(h)

w = hitpoint.normal
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)

alpha = 1.0 / nu
beta = 1.0 / nv

hxa = dot(h, u) / alpha
hyb = dot(h, v) / beta
hdotn = dot(h, w)

exponent = ((hxa * hxa + hyb * hyb) / (hdotn * hdotn)) * -1.0

denom = 4.0 * 3.14159 * alpha * beta * dot(h, shadepoint.wo) * hdotn * hdotn * hdotn

pdf_specular = exp(exponent) / denom
pdf_diffuse = dot(hitpoint.normal, shadepoint.wi) * 0.318309886

shadepoint.pdf = (pdf_specular + pdf_diffuse) * 0.5

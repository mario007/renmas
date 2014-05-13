
h = shadepoint.wo + shadepoint.wi
h = normalize(h)

w = hitpoint.normal
tv = (0.0034, 1.0, 0.0071)
v = cross(tv, w)
v = normalize(v)
u = cross(v, w)

hxa = dot(h, u) / alpha
hyb = dot(h, v) / beta
hdotn = dot(h, w)

exponent = ((hxa * hxa + hyb * hyb) / (hdotn * hdotn)) * -1.0

denom = 4.0 * 3.14159 * alpha * beta * dot(h, shadepoint.wo) * hdotn * hdotn * hdotn

pdf_specular = exp(exponent) / denom
pdf_diffuse = dot(hitpoint.normal, shadepoint.wi) * 0.318309886

shadepoint.pdf = (pdf_specular + pdf_diffuse) * 0.5

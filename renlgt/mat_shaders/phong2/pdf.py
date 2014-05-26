
ndotwi = dot(hitpoint.normal, shadepoint.wi)
r = hitpoint.normal * ndotwi * 2.0 - shadepoint.wi
rdotwo = dot(r, shadepoint.wo)
pdf = 0.0
if rdotwo > 0.0:
    tmp = (exponent + 1.0) * 0.159154943 # 0.159... = 1 / (2 * math.pi)
    pdf = tmp * pow(rdotwo, exponent)

# shadepoint.pdf = (ndotwi * 0.318309886 + pdf) * 0.5
diff_prob = ndotwi * 0.318309886

davg = luminance(diffuse)
savg = luminance(specular)
weight = savg / (davg + savg)
shadepoint.pdf = weight * pdf + (1.0 - weight) * diff_prob

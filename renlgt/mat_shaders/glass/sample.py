
R0 = (ior - 1.0) / (ior + 1.0)
R0 = R0 * R0
k = 0.5
eta = ior

normal = hitpoint.normal
ndotwo = dot(normal, shadepoint.wo)
if ndotwo < 0.0:
    ndotwo = ndotwo * -1.0
    normal = hitpoint.normal * -1.0
    eta = 1.0 / eta

tir = 1.0 - (1.0 - ndotwo * ndotwo) / (eta * eta)
if tir < 0.0: # Total internal reflection occured
    wi = normal * ndotwo * 2.0 - shadepoint.wo
    pdf = 1.0
    reflectance = Spectrum(1.0)
else:
    tmp = dot(normal, shadepoint.wo)
    tmp2 = sqrt(tir)
    if tmp2 > tmp:
        t = 1.0 - tmp2
    else:
        t = 1.0 - tmp

    # wo = shadepoint.wo * -1.0
    # cosine = dot(wo, hitpoint.normal)
    # t = 1.0 - abs(cosine)

    #t = 1.0 - ndotwo
    R = R0 + (1.0 - R0) * t * t * t * t * t
    P = (1.0 - k) * R + 0.5 * k
    rnd = random()

    # P = 0.5
    # R = 0.5

    if rnd < P: # reflection ray
        wi = normal * ndotwo * 2.0 - shadepoint.wo
        pdf = P
        reflectance = Spectrum(1.0) * R
    else: # transmission ray
        wo = shadepoint.wo * -1.0
        wi = wo * (1.0 / eta) - ((sqrt(tir) - ndotwo / eta) * normal)
        #wi = normalize(wi)
        pdf = 1.0 - P
        #reflectance = Spectrum(1.0) * ((1.0 - R) * (1.0 / (eta * eta)))
        reflectance = Spectrum(1.0) * ((1.0 - R) * (eta * eta))


ndotwi = dot(hitpoint.normal, wi)
reflectance = reflectance * (1.0 / abs(ndotwi))

shadepoint.wi = wi
shadepoint.pdf = pdf
shadepoint.material_reflectance = reflectance

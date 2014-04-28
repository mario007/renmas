

normal = hitpoint.normal
incident = shadepoint.wo * -1.0
n1 = 1.0
n2 = ior

ndotwo = dot(normal, shadepoint.wo)
if ndotwo < 0.0:
    normal = normal * -1.0
    n1 = ior
    n2 = 1.0

ret = tir(normal, incident, n1, n2)
if ret == 1:  # TIR ocur
    wi = reflect(normal, incident)
    pdf = 1.0
    reflectance = Spectrum(1.0)
else:
    rnd = random()

    k = 0.5
    R = dielectric_reflectance(normal, incident, n1, n2)
    P = (1.0 - k) * R + 0.5 * k

    if rnd < P: # reflection ray
        wi = reflect(normal, incident)
        pdf = P
        reflectance = Spectrum(1.0) * R
    else: # transmission ray
        wi = refract(normal, incident, n1, n2)
        pdf = 1.0 - P
        T = 1.0 - R
        eta = (n1 * n1) / (n2 * n2)

        reflectance = Spectrum(1.0) * T * eta

ndotwi = dot(hitpoint.normal, wi)
reflectance = reflectance * (1.0 / abs(ndotwi))
shadepoint.specular_bounce = 1

shadepoint.wi = wi
shadepoint.pdf = pdf
shadepoint.material_reflectance = reflectance

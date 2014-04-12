

__light_sample(hitpoint, shadepoint, ptr_light_sample)
__material_emission(hitpoint, shadepoint, ptr_mat_emission)

wi = shadepoint.light_position - hitpoint.hit

len_squared = wi[0] * wi[0] + wi[1] * wi[1] + wi[2] * wi[2]
wi = normalize(wi)

cos_light = dot(shadepoint.light_normal, wi)
if cos_light < 0.0:
    cos_light = cos_light * -1.0

    # weight = cos_light / len_squared
    # shadepoint.light_intensity = shadepoint.material_emission * weight

    shadepoint.light_pdf = shadepoint.light_pdf * len_squared / cos_light
    shadepoint.light_intensity = shadepoint.material_emission
else:
    shadepoint.light_intensity = Spectrum(0.0)
shadepoint.wi = wi

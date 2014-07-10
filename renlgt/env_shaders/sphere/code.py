

wi = position - hitpoint.hit
distance_squared = wi[0] * wi[0] + wi[1] * wi[1] + wi[2] * wi[2]


shadepoint.light_intensity = intensity * (1.0 / distance_squared)
shadepoint.light_position = position
shadepoint.wi = normalize(wi)
shadepoint.light_pdf = 1.0


inv_pi = 0.31830988618
shadepoint.light_intensity = intensity * scale
shadepoint.light_pdf = inv_pi * 0.25



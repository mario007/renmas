
# Point light shader

# input: hitpoint - contains information of intersection point 
# input: shadepoint - contains information of shade point

# Light parameters:
# parameter: position - position of light
# parameter: intensity - radiant intensity of light

# Required output from light shader
# shadepoint.light_intensity - return radiant intensity of light 
# shadepoint.light_position - return point of light
# shadepoint.wi - direction from intersection point to light position

wi = position - hitpoint.hit
distance_squared = wi[0] * wi[0] + wi[1] * wi[1] + wi[2] * wi[2]
shadepoint.light_intensity = intensity * (1.0 / distance_squared)
shadepoint.light_position = position
shadepoint.wi = normalize(wi)

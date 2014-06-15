#hitpoint is argument to shader
#shadepoint is argument to shader
# diffuse is property of shader

width = texture.width
height = texture.height
u = hitpoint.u
v = hitpoint.v

x = width * u
y = height * v
x = int(x)
y = int(y)

if x < 0:
    x = 0
if x >= width:
    x = width - 1

if y < 0:
    y = 0
if y >= height:
    y = height - 1

val = get_rgba(texture, x, y)
val = float3(val[0], val[1], val[2])
shadepoint.material_reflectance = rgb_to_spectrum(val) * 0.318309886

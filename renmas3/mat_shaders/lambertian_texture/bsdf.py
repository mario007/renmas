#hitpoint is argument to shader
#shadepoint is argument to shader
# texture is property of shader

width = texture.width - 1
height = texture.height - 1
u = hitpoint.u
v = hitpoint.v
if u > 1.0:
    u = 0.99999

if v > 1.0:
    v = 0.99999

if u < 0.0:
    u = 0.0

if v < 0.0:
    v = 0.0

x = width * u 
y = height * v

x = int(x)
y = int(y)

if x > width:
    x = width

if y > height:
    y = height
rgba = get_rgba(texture, x, y)
diffuse = rgb_to_spectrum(rgba)
shadepoint.material_reflectance = diffuse * 0.318309886


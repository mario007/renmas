
from tdasm import Runtime
from renmas3.base import ImagePRGBA, arg_map, create_shader, Vec3

arg_map1 = arg_map([('image1', ImagePRGBA), ('value', Vec3)])

img1 = ImagePRGBA(1024, 768)

img1.set_pixel(10, 10, 0.4, 0.3, 0.2)
code = """
value = get_rgb(image1, 10, 10)

color = (0.1, 0.5, 0.6)
set_rgb(image1, 20, 20, color)
"""

shader = create_shader("test", code, arg_map1)
runtimes = [Runtime()]
shader.prepare(runtimes)
shader.set_value('image1', img1)
shader.execute()

print(shader.get_value('value'))
print(img1.get_pixel(20, 20))



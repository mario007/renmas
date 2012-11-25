
import time
from tdasm import Runtime
from renmas3.base import ImagePRGBA, arg_map, create_shader

arg_map1 = arg_map([('image1', ImagePRGBA)])

img1 = ImagePRGBA(1024, 768)

code = """
value = (0.5, 0.5, 0.5)
y = image1.height - 1
while y >= 0:
    x = image1.width - 1
    while x >= 0:
        set_rgb(image1, x, y, value)
        x = x - 1
    y = y - 1
"""
shader = create_shader("test", code, arg_map1)
runtimes = [Runtime()]
shader.prepare(runtimes)
shader.set_value('image1', img1)

start = time.clock()
shader.execute()
end = time.clock()
print("Execution time of shader = ", end-start)

start = time.clock()
for y in range(img1.height):
    for x in range(img1.width):
        img1.set_pixel(x, y, 0.5, 0.5, 0.5)
end = time.clock()
print("Execution time of python = ", end-start)


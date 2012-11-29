
from tdasm import Runtime
from renmas3.base import ImagePRGBA
import renmas3.base
from renmas3.base import create_shader, create_argument, create_user_type
from renmas3.base import arg_map, arg_list
from renmas3.base import register_user_type
from renmas3.base import Vector3


point = create_user_type(typ="point", fields=[('x', 10), ('y', 20)])
size = create_user_type(typ="size", fields=[('w', 0.0), ('h', 0.0), ('k', (3,4,5))])
register_user_type(point)
register_user_type(size)

arg_map1 = arg_map([('p1', 3), ('p2', 4), ('ps', point), ('pm', point),('p3', 0.3),
    ('p4', (4,5,6)), ('rect', size), ('slika', ImagePRGBA)])

code = """
p1 = 484
ps.x = 14
p3 = 3.3
p4 = (92,3,3)
p5 = 55
p1 = ps.x
p7 = 8.8
p3 = p7
pm.x = ps.y
p11 = (6,7,8)
p4 = p11
p3 = p1
rect.w = 4.4
rect.h = p3 
rect.k = [6,7,8]
ps.x = int(p7)
p3 = ret_arg(p5)
p5 = 22
p55 = 9.3
p66 = (6,7,8)
rect.w = p55
rect.k = - p66
p1 = 78 
while p1 < 100:
    p1 = p1 + 1
    if p1 > 96.8:
        break
nn = (2.2, 1.1, 3.4)
set_rgb(slika, 1, 2, nn)
rect.k = get_rgb(slika, 1, 2)
rect.w = pow(rect.w, 3.3)
p1 = int(3) + 4
"""

code2 = """
#p1 is input argument
p2 = p1 
return p2
"""
arg_lst = arg_list([('p1', 3)])
arg_map2 = arg_map([])
shader2 = create_shader("ret_arg", code2, arg_map2, arg_lst, func=True)

runtimes = [Runtime()]
shader = create_shader("test", code, arg_map1, shaders=[shader2])
shader.prepare(runtimes)

img = ImagePRGBA(3,3)
img.set_pixel(1, 2, 0.2, 0.3, 0.1)
shader.set_value('slika', img)
shader.execute()

print(shader.get_value('p1'))
print(shader.get_value('ps.x'))
print(shader.get_value('pm.x'))
print(shader.get_value('p3'))
print(shader.get_value('p4'))
print(shader.get_value('rect.w'))
print(shader.get_value('rect.h'))
print(shader.get_value('rect.k'))
print(shader.get_value('slika.width'))
print(shader.get_value('slika.height'))
print(shader.get_value('slika.pitch'))
print(shader.get_value('slika.pixels'))



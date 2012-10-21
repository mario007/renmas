
from tdasm import Runtime
from renmas3.core import ImageFloatRGBA
import renmas3.osl
from renmas3.osl import create_shader, create_argument, create_user_type
from renmas3.osl import arg_map, arg_list
from renmas3.osl import register_user_type
from renmas3.core import Vector3


point = create_user_type(typ="point", fields=[('x', 10), ('y', 20)])
size = create_user_type(typ="size", fields=[('w', 0.0), ('h', 0.0), ('k', (3,4,5))])
register_user_type(point)
register_user_type(size)

im_arg = create_argument('ds', typ=ImageFloatRGBA)
register_user_type(im_arg.typ)

arg_map1 = arg_map([('p1', 3), ('p2', 4), ('ps', point), ('pm', point),('p3', 0.3),
    ('p4', (4,5,6)), ('rect', size), ('slika', ImageFloatRGBA)])

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
rect.w = -p55
rect.k = - p66
p1 = 78 
while p1 < 100:
    p1 = p1 + 1
    if p1 > 96.8:
        break
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
shader.execute()

img = ImageFloatRGBA(3,3)
#shader.set_value('slika', img)

print(shader.get_value('p1'))
print(shader.get_value('ps.x'))
print(shader.get_value('pm.x'))
print(shader.get_value('p3'))
print(shader.get_value('p4'))
print(shader.get_value('rect.w'))
print(shader.get_value('rect.h'))
print(shader.get_value('rect.k'))


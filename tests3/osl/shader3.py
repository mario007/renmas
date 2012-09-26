
from tdasm import Runtime
import renmas3.osl
from renmas3.osl import create_shader, create_argument, create_user_type
from renmas3.osl import create_argument_map, create_argument_list
from renmas3.osl import register_user_type
from renmas3.core import Vector3

point = create_user_type(typ="point", fields=[('x', 10), ('y', 20)])
register_user_type(point)
arg_map = create_argument_map([('p1', 3), ('p2', 4), ('ps', point), ('pm', point),('p3', 0.3),
    ('p4', (4,5,6))])

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
"""

runtimes = [Runtime()]
shader = create_shader("test", code, arg_map)
shader.prepare(runtimes)
shader.execute()

print(shader.get_value('p1'))
print(shader.get_value('ps.x'))
print(shader.get_value('pm.x'))
print(shader.get_value('p3'))
print(shader.get_value('p4'))


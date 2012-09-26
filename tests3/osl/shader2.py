
from tdasm import Runtime
import renmas3.osl
from renmas3.osl import create_shader, create_argument, create_struct_argument
from renmas3.core import Vector3


a1 = create_argument('p1', 2)
a2 = create_argument('p2', 1)
a3 = create_argument('p3', 5.0)
#a4 = create_argument('p4', Vector3(2,5,6))
a4 = create_argument('p4', [2,5,6])
a5 = create_struct_argument(typ="point", name="ps", fields=[('x', 5.5), ('y', (4,5,6))])
a6 = create_argument('p6', 99)
a7 = create_argument('p7', 8.3)
a8 = create_argument('p8', (4,5,6))
args = {a1.name:a1, a2.name: a2, a3.name: a3, a4.name: a4, a5.name: a5}
code = """
ps.x = 8.33
ps.y = (9,9,8)
p2 = p6
"""

shader = create_shader("test", code, args, input_args=[a6], func=True)

runtimes = [Runtime()]
shader.prepare(runtimes)

m1 = create_argument('m1', 2)
code2 = """
a = 44
test(a)
"""
args2 = {m1.name:m1}
shader2 = create_shader("test2", code2, args2, shaders=[shader], func=False)
shader2.prepare(runtimes)

#shader.execute()
shader2.execute()


print(shader.get_value('p1'))
print(shader.get_value('p2'))
print(shader.get_value('p3'))
print(shader.get_value('p4'))
print(shader.get_value('ps.x'))
print(shader.get_value('ps.y'))


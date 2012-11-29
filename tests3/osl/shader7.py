
from tdasm import Runtime
from renmas3.base import create_shader, arg_map, Integer, Float, Vec3
from renmas3.base import create_function, arg_list

arg_map1 = arg_map([('v1', Vec3), ('v2', Vec3), ('f1', Float), ('i1', Integer)])
code = """
p3 = (3.4, 3.3, 2.2)
v1 = p3
mm = 4.4
f1 = mm
gg = 44
i1 = gg
"""
shader = create_shader("test", code, arg_map1)
print (shader._code)
runtimes = [Runtime()]
shader.prepare(runtimes)
shader.execute()

print(shader.get_value('v1'))
print(shader.get_value('v2'))
print(shader.get_value('f1'))
print(shader.get_value('i1'))


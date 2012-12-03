
from tdasm import Runtime
from renmas3.base import create_shader, arg_map, Integer, Float, Vec3
from renmas3.base import create_function, arg_list

runtimes = [Runtime()]
code2 = """
#input a = float, b = int
a = b
return a
"""
arg_lst1 = arg_list([('a', Float), ('b', Integer)])
sh1 = create_function('conv_int', code2, input_args=arg_lst1)
sh1.prepare(runtimes)


arg_map1 = arg_map([('a', Integer), ('b', Float), ('c', Vec3),
    ('f', Vec3)])
code = """
a = 2
b = 2.2
c = (2, 3, 4)
f = [6,7,7.7]
b = conv_int(b, a)
int(55)
b = 3 + pow(2,3) * 2.5
#b = pow(2,3) * 2.5 + 3
"""


shader = create_shader("test", code, arg_map1, shaders=[sh1])
shader.prepare(runtimes)
shader.execute()
print (shader._code)

print(shader.get_value('a'))
print(shader.get_value('b'))
print(shader.get_value('c'))
print(shader.get_value('f'))


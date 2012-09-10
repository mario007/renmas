
from tdasm import Runtime
import renmas3.osl
from renmas3.osl import create_shader, create_argument


a1 = create_argument('p1', 2)
a2 = create_argument('p2', 1)
a3 = create_argument('p3', 5.0)
args = {a1.name:a1, a2.name: a2, a3.name: a3}
code = """
p3 = 2 + 7

"""

shader = create_shader(code, args)

runtimes = [Runtime()]
shader.prepare(runtimes)

shader.execute()


print(shader.get_value('p1'))
print(shader.get_value('p2'))
print(shader.get_value('p3'))


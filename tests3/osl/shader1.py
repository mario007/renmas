
import renmas3.osl
from renmas3.osl import create_shader, IntArg, FloatArg

a1 = FloatArg('p1', 2)
code = 'a = b'
args = {a1.name:a1}

shader = create_shader(code, args)
print(shader)


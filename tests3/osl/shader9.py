
from tdasm import Runtime
from renmas3.base import BasicShader

code = """
a = 555
"""

def py_code(props):
    props['a'] = 555

props = {'a':125}
bs = BasicShader(code, py_code, props)
runtime = Runtime()
bs.prepare([runtime])

bs.execute()
print(bs.shader.get_value('a'))

bs.execute_py()
print(props['a'])


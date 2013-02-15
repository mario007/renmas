
from tdasm import Runtime
from renmas3.base import BasicShader

code = """
a = 555
"""

props = {'a':125}
bs = BasicShader(code, props)
runtime = Runtime()
bs.prepare([runtime])

bs.execute()
print(bs.shader.get_value('a'))


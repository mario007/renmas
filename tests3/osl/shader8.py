
from tdasm import Runtime
from renmas3.base import GeneralShader, Float, Integer

def assign(props):
    props.set_value('p1', 33)

code = """
    p1 = 33
"""

sh = GeneralShader('reinhard', code=code, py_code=assign)
sh.props.add([Integer('p1')])

runtimes = [Runtime()]
sh.prepare(runtimes)

sh.execute_py()
#sh.execute()

print(sh.props.get_value('p1'))


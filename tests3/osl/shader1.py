
from tdasm import Runtime
import renmas3.osl
from renmas3.osl import Shader, create_argument

a1 = create_argument('aa', 2)
a2 = create_argument('bb', 3.3)
args = {a1.name:a1, a2.name: a2}

cgen = renmas3.osl.CodeGenerator(args)
stm = renmas3.osl.StmAssignConst(cgen, 'aa', 5)
stm2 = renmas3.osl.StmAssignConst(cgen, 'ac', 12)
stm3 = renmas3.osl.StmAssignConst(cgen, 'bb', 2.33)
cgen.add_stm(stm)
cgen.add_stm(stm2)
cgen.add_stm(stm3)
code = cgen.generate_code()
print(code)

shader = Shader(code, args)
runtimes = [Runtime()]
shader.prepare(runtimes)
shader.execute()

print(shader.get_value('aa'))
print(shader.get_value('bb'))

# shader.prepare(runtimes)
# shader.execute()

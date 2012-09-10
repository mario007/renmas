import x86
from tdasm import Tdasm
from .parser import Parser

class Shader:
    def __init__(self, code, args):
        self._code = code
        self._args = args
        self._ds = []

    def prepare(self, runtimes):
        self._ds = []
        asm = Tdasm()
        mc = asm.assemble(self._code)
        #mc.print_machine_code()
        name = 'shader' + str(id(self))
        self._runtimes = runtimes
        for r in runtimes:
            self._ds.append(r.load(name, mc)) 

    def execute(self):
        name = 'shader' + str(id(self))
        addrs = [r.address_module(name) for r in self._runtimes]
        x86.ExecuteModules(tuple(addrs))

    def get_value(self, name, idx_thread=None):
        return self._args[name].get_value(self._ds, idx_thread)

    def set_value(self, name, value, idx_thread=None):
        return self._args[name].set_value(self._ds, value, idx_thread)

def create_shader(source, args, input_args=None, functions=None, shaders=None):

    parser = Parser()
    cgen = parser.parse(source, args)
    code = cgen.generate_code()
    print(code)
    shader = Shader(code, args)

    return shader


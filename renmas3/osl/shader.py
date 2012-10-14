import x86
from tdasm import Tdasm
from .arg import StructArg

class Shader:
    def __init__(self, name, code, args, input_args=[], shaders=[],
            ret_type=None, func=False):
        self._name = name
        self._code = code
        self._args = args
        self._input_args = input_args
        self._shaders = shaders
        self._ret_type = ret_type
        self._ds = []
        self._struct_args = {}
        self._func = func 
        for key, arg in iter(args):
            if isinstance(arg, StructArg):
                self._struct_args.update(arg.paths)

    @property
    def ret_type(self):
        return self._ret_type

    @property
    def name(self):
        return self._name

    @property
    def input_args(self):
        return self._input_args

    def prepare(self, runtimes):
        for s in self._shaders:
            s.prepare(runtimes)
        self._ds = []
        asm = Tdasm()
        mc = asm.assemble(self._code, self._func)
        #mc.print_machine_code()
        name = 'shader' + str(id(self))
        self._runtimes = runtimes
        for r in runtimes:
            #TODO check if shader allread exist in runtime
            #TODO if shader is function load it as function
            self._ds.append(r.load(name, mc)) 

    def execute(self):
        if len(self._runtimes) == 1:
            name = 'shader' + str(id(self))
            self._runtimes[0].run(name)
        else:
            name = 'shader' + str(id(self))
            addrs = [r.address_module(name) for r in self._runtimes]
            x86.ExecuteModules(tuple(addrs))

    def get_value(self, name, idx_thread=None):
        if name in self._args:
            return self._args[name].get_value(self._ds, idx_thread)
        elif name in self._struct_args:
            return self._struct_args[name].get_value(self._ds, path=name, idx_thread=idx_thread)
        else:
            raise ValueError("Wrong name of argument", name)

    def set_value(self, name, value, idx_thread=None):
        return self._args[name].set_value(self._ds, value, idx_thread)



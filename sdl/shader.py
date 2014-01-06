"""
    Implementation of Shader that is used for compiling and
    exectuing shader.
"""

import x86
from tdasm import Tdasm
from .parser import parse
from .cgen import CodeGenerator
from .args import ArgList
from .ext_func import load_ext_function


class Shader:
    def __init__(self, code, args=[], is_func=False,
                 name=None, func_args=[]):

        self._code = code
        self._args = args
        self._is_func = is_func
        if is_func and name is None:
            raise ValueError("Function shader must have name!")

        self._name = name
        self._func_args = func_args

        self._ds = None
        self._args_map = {}
        for arg in self._args:
            self._args_map[arg.name] = arg

        self._ret_type = None

    @property
    def ret_type(self):
        return self._ret_type

    @property
    def name(self):
        return self._name

    @property
    def func_args(self):
        return self._func_args

    def compile(self, shaders=[]):
        stms = parse(self._code)
        cgen = CodeGenerator()
        asm, ret_type, fns = cgen.generate_code(stms, args=self._args,
                                                is_func=self._is_func,
                                                name=self._name,
                                                func_args=self._func_args,
                                                shaders=shaders)
        self._asm_code = asm
        self._ret_type = ret_type
        self._ext_functions = fns
        asm = Tdasm()
        self._mc = asm.assemble(self._asm_code, naked=self._is_func,
                                ia32=not cgen.BIT64)

    def prepare(self, runtimes):
        for fn in self._ext_functions.values():
            load_ext_function(runtimes, fn)

        name = 'shader' + str(id(self))
        self._ds = [r.load(name, self._mc) for r in runtimes]
        self._runtimes = runtimes

        self.update_args()

    def get_ptrs(self):
        if not self._is_func:
            raise ValueError("Only function shader can have function pointers!")
        ptrs = [r.address_label(self._name) for r in self._runtimes]
        return ptrs

    def update_args(self):
        if self._ds is None:
            return
        for arg in self._args:
            self._update_arg(arg)

    def _update_arg(self, arg):
        if isinstance(arg, ArgList):
            arg.update(self._ds)
        else:
            for ds in self._ds:
                arg.update(ds)

    def _get_arg(self, name):
        return self._args_map[name]

    def set_value(self, name, value):
        arg = self._get_arg(name)
        arg.value = value
        if self._ds is not None:
            self._update_arg(arg)

    def get_value(self, name):
        arg = self._get_arg(name)
        if self._ds is None:
            return arg.value
        if isinstance(arg, ArgList):
            return arg.from_ds(self._ds)
        else:
            return arg.from_ds(self._ds[0])

    def execute(self):
        if self._is_func:
            raise ValueError("Function shader cannot be directly executed.")
        name = 'shader' + str(id(self))
        if len(self._runtimes) == 1:
            self._runtimes[0].run(name)
        else:
            addrs = [r.address_module(name) for r in self._runtimes]
            x86.ExecuteModules(tuple(addrs))

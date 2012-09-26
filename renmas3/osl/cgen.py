import copy

from .arg import create_argument, StructArg, IntArg, FloatArg, Vector3Arg
from .shader import Shader

_user_types = {}

def register_user_type(typ):
    if typ.typ in _user_types:
        pass #TODO -- check if two types are compatabile
    else:
        _user_types[typ.typ] = typ

def _copy_from_regs(args):
    xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    for a in args:
        if isinstance(a, IntArg):
            code += "mov dword [%s], %s \n" % (a.name, general.pop())
        elif isinstance(a, FloatArg):
            code += "movss dword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, Vector3Arg):
            code += "movaps oword [%s], %s \n" % (a.name, xmm.pop())
        else:
            raise ValueError('Unknown argument', a)
    return code


class CodeGenerator:
    def __init__(self, name, args={}, input_args=[], shaders=[], func=False):
        self._name = name
        self._args = args
        self._input_args =  input_args
        self._shaders = shaders
        self._func = func
        self._statements = []

    def is_input_arg(self, arg):
        return arg in self._input_args

    def add(self, stm):
        self._statements.append(stm)

    def _generate_data_section(self):
        data = ''
        #TODO remove duplicates, struct inside sturct
        for typ_name, typ in _user_types.items():
            data += typ.generate_struct()

        for arg in self._input_args:
            data += arg.generate_data()

        for name, arg in iter(self._args):
            data += arg.generate_data()

        for arg in self._locals.values():
            data += arg.generate_data()
        return data

    def generate_code(self):
        self._locals = {}
        code = ''
        for s in self._statements:
            self.clear_regs()
            code += s.asm_code()
        data = self._generate_data_section() + '\n'
        data = "\n#DATA \n" + data + "#CODE \n"
        glo = ''
        if self._func:
            glo = "global %s:\n" % self._name
        code = glo + _copy_from_regs(self._input_args) + code
        if self._func:
            code += "ret\n"
        return data + code + '#END \n'

    def create_shader(self):
        code = self.generate_code()
        print (code)
        shader = Shader(self._name, code, self._args, self._input_args, self._shaders)
        return shader

    #create const it it's doesnt exist
    def create_const(self, value):
        pass

    def get_argument(self, name, path=None):
        arg = None
        if name in self._args:
            arg = self._args[name]
        if name in self._locals:
            arg =  self._locals[name]
        for a in iter(self._input_args):
            if name == a.name:
                arg = a
                break
        if path is not None:
            if isinstance(arg, StructArg):
                full_path = name + '.' + path
                arg = arg.get_argument(full_path)
        return arg

    def create_local(self, name, value, path=None):
        if path is not None: #struct member
            arg = self.get_argument(name)
            if arg is None:
                raise ValueError("Structure %s doesnt exist" % name)
            if not isinstance(arg, StructArg):
                raise ValueError("Argument is expected to be struct member.", arg)
            full_path = name + '.' + path
            a = arg.get_argument(full_path)
            if a is None:
                raise ValueError("Struct member %s doesnt exist" % full_path)
            return a
        
        arg = self.get_argument(name)
        if arg is not None:
            return arg

        #create new local argument
        if isinstance(value, str): # a = b --- create argument a that have same type as b
            arg =  self.get_argument(value)
            if arg is None:
                raise ValueError("Argument %s doesnt exist" % value)
            if isinstance(arg, StructArg):
                if arg.typ.typ not in _user_types:
                    raise ValueError("User type %s is not registerd." % arg.typ.typ)
                arg = create_argument(name, arg.typ)
                self._locals[name] = arg
                return arg
            value = copy.deepcopy(arg.value)
        arg = create_argument(name, value)
        self._locals[name] = arg
        return arg

    def func_exist(self, name):
        for shader in self._shaders:
            if name == shader.name:
                return True
        return False 

    def input_args(self, name):
        for shader in self._shaders:
            if name == shader.name:
                return shader.input_args
        return None

    def fetch_register(self, reg_type):
        if reg_type == 'xmm':
            return self._xmm.pop()
        elif reg_type == 'general':
            return self._general.pop()
        else:
            raise ValueError('Unknown type of register', reg_type)

    def fetch_register_exact(self, reg):
        if reg in self._xmm:
            self._xmm.remove(reg)
            return reg
        if reg in self._general:
            self._general.remove(reg)
            return reg
        return None

    # clear ocupied registers
    def clear_regs(self):
        self._xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        self._general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']

    def type_of(self, name, path=None):
        if path is not None: #struct members
            arg = None
            if name in self._args:
                arg = self._args[name]
            if name in self._locals:
                arg = self._locals[name]
            if arg is None or not isinstance(arg, StructArg):
                return None
            a = arg.get_argument(name + "." + path)
            if a is not None:
                return type(a)
            else:
                return None

        if name in self._args:
            return type(self._args[name])
        if name in self._locals:
            return type(self._locals[name])
        for a in self._input_args:
            if a.name == name:
                return type(a)
        return None


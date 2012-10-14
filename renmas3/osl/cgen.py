import copy
import platform
from .arg import create_argument, StructArg, IntArg, FloatArg, Vector3Arg, UserType, Attribute
from .arg import ConstIntArg, ConstFloatArg, ConstVector3Arg, ConstVector3IntsArg
from .shader import Shader
from ..core import Vector3

_user_types = {}
_built_in_functions = {}

def register_function(name, func, return_type, inline=False):
    _built_in_functions[name] = (func, return_type, inline)

def register_user_type(typ):
    if typ.typ in _user_types:
        pass #TODO -- check if two types are compatabile
    else:
        _user_types[typ.typ] = typ

def _copy_from_regs(args):
    xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    bits = platform.architecture()[0]
    for a in args:
        if isinstance(a, IntArg):
            code += "mov dword [%s], %s \n" % (a.name, general.pop())
        elif isinstance(a, FloatArg):
            code += "movss dword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, Vector3Arg):
            code += "movaps oword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, StructArg):
            if bits == '64bit':
                reg = general.pop()
                reg = 'r' + reg[1:]
                code += "mov qword [%s], %s \n" % (a.name, reg)
            else:
                code += "mov dword [%s], %s \n" % (a.name, general.pop())
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
        self._ret_type = None
        self._constants = {}
        self._counter = 0

    def is_input_arg(self, arg):
        return arg in self._input_args

    def is_user_type(self, name):
        return name in _user_types

    def is_inline_func(self, name):
        if name in _built_in_functions:
            return _built_in_functions[name][2]
        return False

    def add(self, stm):
        self._statements.append(stm)

    def register_ret_type(self, typ):
        if self._ret_type is None:
            self._ret_type = typ
        if self._ret_type != typ:
            raise ValueError("Return Type mismatch ", self._ret_type, typ)

    def _generate_data_section(self):
        data = ''
        #TODO remove duplicates, struct inside sturct
        for typ_name, typ in _user_types.items():
            data += typ.generate_struct()

        for arg in self._input_args:
            if isinstance(arg, StructArg):
                if self.is_input_arg(arg):
                    data += arg.generate_data(True)
                else:
                    data += arg.generate_data()
            else:
                data += arg.generate_data()

        for name, arg in iter(self._args):
            data += arg.generate_data()

        for arg in self._locals.values():
            data += arg.generate_data()

        for arg in self._constants.values():
            data += arg.generate_data()

        return data

    def generate_code(self):
        self._locals = {}
        self._constants = {}
        self._ret_type = None
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
        if self._func:
            return data + code
        else:
            return data + code + '#END \n'

    def create_shader(self):
        code = self.generate_code()
        print (code)
        shader = Shader(self._name, code, self._args, self._input_args,
                self._shaders, self._ret_type, self._func)
        return shader

    #create const it it's doesnt exist
    def create_const(self, value):
        if value in self._constants:
            return self._constants[value]
        if isinstance(value, int):
            arg = ConstIntArg(self._generate_name('const'), value)
        elif isinstance(value, float):
            arg = ConstFloatArg(self._generate_name('const'), value)
        elif isinstance(value, list) or isinstance(value, tuple):
            if len(value) == 3:
                v = value
                if isinstance(v[0], int) and isinstance(v[1], int) and isinstance(v[2], int):
                    arg = ConstVector3IntsArg(self._generate_name('const'), value)
                else:
                    v = Vector3(float(value[0]), float(value[1]), float(value[2]))
                    arg = ConstVector3Arg(self._generate_name('const'), v)
            else:
                raise ValueError("Not yet implemented that type of constant", value)
        else:
            raise ValueError("Unknown type of value", value)
        self._constants[value] = arg
        return arg

    def _generate_name(self, prefix=''):
        name = prefix + '_' + str(self._counter) + str(id(self))
        self._counter += 1
        return name

    def get_arg(self, src):
        arg = None
        path = None
        if isinstance(src, Attribute):
            name = src.name
            path = src.path
        else:
            name = src

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

    def create_arg(self, dest, value=None, typ=None):
        if isinstance(dest, Attribute):
            name = dest.name
            path = dest.path
        else:
            name = dest
            path = None

        if typ is not None:
            arg = self.get_arg(dest)
            if arg is not None:
                return arg
            if typ == IntArg:
                arg = IntArg(name)
            elif typ == FloatArg:
                arg = FloatArg(name)
            elif typ == Vector3Arg:
                arg = Vector3Arg(name, Vector3(0.0, 0.0, 0.0))
            elif typ == UserType:
                if typ.typ not in _user_types:
                    raise ValueError("Unregister type %s is not registerd." % typ.typ)
                arg = StructArg(name, typ)
            elif isinstance(typ, str):
                if typ not in _user_types:
                    raise ValueError("Unregister type %s is not registerd." % typ)
                arg = StructArg(name, _user_types[typ])
            else:
                raise ValueError("Unknown argument!!!", typ)
            self._locals[name] = arg
            return arg
        if path is not None: #struct member
            arg = self.get_arg(name)
            if arg is None:
                raise ValueError("Structure %s doesnt exist" % name)
            if not isinstance(arg, StructArg):
                raise ValueError("Argument is expected to be struct member.", arg)
            full_path = name + '.' + path
            a = arg.get_argument(full_path)
            if a is None:
                raise ValueError("Struct member %s doesnt exist" % full_path)
            return a
        
        arg = self.get_arg(name)
        if arg is not None:
            return arg

        #create new local argument
        if isinstance(value, str): # a = b --- create argument a that have same type as b
            arg =  self.get_arg(value)
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
        
    def get_shader(self, name):
        for shader in self._shaders:
            if name == shader.name:
                return shader
        return None

    def get_function(self, name):
        if name in _built_in_functions:
            return _built_in_functions[name]
        return None

    def register(self, typ=None, bit=32, reg=None):
        assert typ is not None or reg is not None
        if reg is not None and reg in self._xmm:
            self._xmm.remove(reg)
            return reg
        if reg is not None :
            if reg in self._general:
                self._general.remove(reg)
                self._general64.remove('r' + reg[1:])
                return reg
            if reg in self._general64:
                self._general64.remove(reg)
                self._general.remove('e' + reg[1:])
                return reg
        
        if reg is not None:
            raise ValueError("Register %s is ocupied and could not be obtained!" % reg)

        if typ == 'xmm':
            return self._xmm.pop()
        elif typ == 'general':
            if bit == 32:
                self._general64.pop()
                return self._general.pop()
            else:
                self._general.pop()
                return self._general64.pop()
        else:
            raise ValueError('Unknown type of register', typ)

    def release_reg(self, reg):
        if reg in self._xmm or reg in self._general or reg in self._general64:
            return
        xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        if reg in xmm:
            self._xmm.append(reg)
            return
        general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
        if reg in general:
            self._general.append(reg)
            self._general64.append('r' + reg[1:])
            return
        general64 = ['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax']
        if reg in general64:
            self._general64.append(reg)
            self._general.append('e' + reg[1:])

    # clear ocupied registers
    def clear_regs(self):
        self._xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        self._general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
        self._general64 = ['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax']


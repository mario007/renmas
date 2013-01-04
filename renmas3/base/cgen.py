import platform
import inspect
import renmas3.switch as proc

from .arg import create_argument, Struct, Integer, Float, Vec3, UserType, Attribute
from .arg import Integer, Vec3I, Pointer, StructPtr, Name, Const, Subscript
from .arg import Callable, create_user_type
from .shader import Shader
from .vector3 import Vector3
from .instr import load_operand, load_func_args, store_func_args

_user_types = {}
_built_in_functions = {}

def register_function(name, func, inline=False):
    _built_in_functions[name] = (func, inline)

def register_user_type(typ):
    if isinstance(typ, UserType):
        if typ.typ in _user_types:
            pass #TODO -- check if two types are compatabile
        else:
            _user_types[typ.typ] = typ
        return

    if not inspect.isclass(typ):
        raise ValueError("Type is not class", typ)
    if not hasattr(typ, 'user_type'):
        raise ValueError("Class does not have user_type metod defined", typ)

    typ_name, fields = typ.user_type()
    usr_type = create_user_type(typ_name, fields)
    if usr_type.typ in _user_types:
        pass #TODO -- check if two types are compatabile
    else:
        _user_types[usr_type.typ] = usr_type

class Registers:
    def __init__(self):
        self._xmm = ('xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0')
        self._general32 = ('ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax')
        self._general64 = ('rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax')

    def is_xmm(self, reg):
        return reg in self._xmm

    def is_reg32(self, reg):
        return reg in self._general32

    def is_reg64(self, reg):
        return reg in self._general64

    def type(self, reg):
        if reg in self._xmm:
            return 'xmm'
        if reg in self._general32 or reg in self._general64:
            return 'general'
        raise ValueError("Unknown register!", reg)

class _Locals:
    def __init__(self):
        self._free_args = {}
        self._used_args = {}

    def _move_to_free_args(self, arg):
        if type(arg) not in self._free_args:
            self._free_args[type(arg)] = set()
        self._free_args[type(arg)].add(arg)

    def _get_free_arg(self, arg_type):
        if arg_type in self._free_args:
            try:
                return self._free_args[arg_type].pop()
            except KeyError:
                return None
        return None

    def get_arg(self, name):
        if name in self._used_args:
            return self._used_args[name]
        return None

    def generate_data(self):
        data = ''
        for name, arg in self._used_args.items():
            data += arg.generate_data()

        for arg_type, s in self._free_args.items():
            for arg in s:
                data += arg.generate_data()
        return data

    def add(self, name, arg):
        loc_arg = self.get_arg(name)
        if loc_arg is not None and type(loc_arg) == type(arg):
            return loc_arg

        if loc_arg is not None:
            self._move_to_free_args(loc_arg)

        loc_arg = self._get_free_arg(type(arg))
        if loc_arg is None:
            loc_arg = arg

        self._used_args[name] = loc_arg
        return loc_arg 

    def __contains__(self, name):
        return name in self._used_args

    def __getitem__(self, name):
        return self._used_args[name]

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
        self._asm_functions = {}
        self._saved_regs = set()
        self.regs = Registers()

    @property
    def AVX(self):
        return proc.AVX

    def is_user_type(self, obj):
        if isinstance(obj, str):
            return obj in _user_types
        elif isinstance(obj, Callable):
            return obj.name in _user_types
        else:
            raise ValueError("Callable or name is expected as argument", obj)

    def is_inline(self, obj):
        if isinstance(obj, Callable):
            if obj.name in _built_in_functions:
                return _built_in_functions[obj.name][1]
            return False
        else:
            raise ValueError("Callable is expected!", obj)

    def generate_callable(self, obj):
        if not isinstance(obj, Callable):
            raise ValueError("Callable is expected!", obj)

        shader = self.get_shader(obj.name)
        if shader is not None:
            self.clear_regs()
            arg_types = [type(arg) for arg in shader.input_args]
            code = load_func_args(self, obj.args, arg_types)
            self.clear_regs()
            code += "call %s\n" % obj.name
            typ = shader.ret_type
            #TODO cover all possible return types
            if typ == Integer:
                reg = 'eax'
            else:
                reg = 'xmm0'
            self.register(reg=reg)
            return code, reg, typ

        function = self.get_function(obj.name)
        if function is not None:
            func, inline = function
            if not inline:
                self.clear_regs()
            code, reg, typ = func(self, obj.args)
            if not inline:
                self.clear_regs()
                self.register(reg=reg)
            return code, reg, typ

        raise ValueError("Callable %s doesn't exist." % obj.name)

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
        # Only generate struct that are used in current program TODO
        for typ_name, typ in _user_types.items():
            data += typ.generate_struct()

        for arg in self._input_args:
            data += arg.generate_data()

        for name, arg in iter(self._args):
            data += arg.generate_data()

        data += self._locals.generate_data()
        #for arg in self._locals.values():
        #    data += arg.generate_data()

        for arg in self._constants.values():
            data += arg.generate_data()

        for ds_reg in self._saved_regs:
            data += ds_reg

        return data

    def generate_code(self):
        #self._locals = {}
        self._locals = _Locals()

        self._constants = {}
        self._ret_type = None
        code = ''
        for s in self._statements:
            self.clear_regs()
            code += s.asm_code(self)
        data = self._generate_data_section() + '\n'
        data = "\n#DATA \n" + data + "#CODE \n"
        glo = ''
        if self._func:
            glo = "global %s:\n" % self._name
        code = glo + store_func_args(self, self._input_args) + code
        if self._func:
            return data + code + 'ret\n'
        else:
            return data + code + '#END \n'

    def create_shader(self):
        code = self.generate_code()
        shader = Shader(self._name, code, self._args, self._input_args,
                self._shaders, self._ret_type, self._func,
                functions=self._asm_functions)
        return shader

    #create const it it's doesnt exist
    #TODO improve this
    def create_const(self, value):
        if value in self._constants:
            return self._constants[value]
        if isinstance(value, list) or isinstance(value, tuple):
            if len(value) == 3:
                v = value
                if isinstance(v[0], int) and isinstance(v[1], int) and isinstance(v[2], int):
                    arg = Vec3I(self._generate_name('const'), v[0], v[1], v[2])
                else:
                    v = Vector3(float(value[0]), float(value[1]), float(value[2]))
                    arg = Vec3(self._generate_name('const'), v)
            else:
                raise "Curently only constants of length 3 is suported for now!!!" #TODO
        arg = create_argument(self._generate_name('const'), value=value)
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
        elif isinstance(src, Name):
            name = src.name 
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
        if path is not None: #NOTE fixed arg test this
            if isinstance(arg, Struct):
                full_path = arg.name + '.' + path
                arg = arg.get_argument(full_path)
        return arg

    def _is_fixed_name(self, name):
        if name in self._args:
            return True
        for a in iter(self._input_args):
            if name == a.name:
                return True
        return False

    def _create_arg_from_callable(self, src, obj):
        #TODO FIXME sample = Sample() -- sample is argument it means it is fixed structure
        arg = self.get_arg(src)
        if arg is not None and isinstance(arg, Struct):
            if arg.typ.typ == obj.name:
                return arg
                #raise ValueError("Type mismatch", arg.typ.typ, obj.name)
        if obj.name not in _user_types:
            raise ValueError("Unregistered type %s is not registerd." % obj.name)

        if arg is None:
            arg = Struct(self._generate_name('local'), _user_types[obj.name])

        if self._is_fixed_name(arg.name):
            return arg

        arg = self._locals.add(src, arg)
        return arg


    def create_arg(self, dest, value=None, typ=None):
        if isinstance(dest, Name):
            dest = dest.name
        if isinstance(value, Callable):
            return self._create_arg_from_callable(dest, value)
        arg = self.get_arg(dest)
        if arg is not None:
            if type(arg) == typ or self._is_fixed_name(arg.name):
                return arg
        if isinstance(dest, Attribute):
            if arg is not None:
                return arg
            raise ValueError("Cannot create local argument for attribut!")

        if isinstance(value, str): # a = b --- create argument a that have same type as b
            arg2 = self.get_arg(value)
            if isinstance(arg2, Struct):
                arg = create_argument(self._generate_name('local'), value=arg2.typ)
            else:
                arg = create_argument(self._generate_name('local'), typ=type(arg2))
        else:
            arg = create_argument(self._generate_name('local'), value=value, typ=typ)
        if isinstance(arg, Struct): #automatic registration!!!! think TODO
            if arg.typ.typ not in _user_types:
                raise ValueError("User type %s is not registerd." % arg.typ.typ)

        arg = self._locals.add(dest, arg)
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
        if self.regs.is_xmm(reg) and reg not in self._xmm:
            self._xmm.append(reg)
        elif self.regs.is_reg32(reg) and reg not in self._general:
            self._general.append(reg)
            self._general64.append('r' + reg[1:])
        elif self.regs.is_reg64(reg) and reg not in self._general64:
            self._general64.append(reg)
            self._general.append('e' + reg[1:])


    # clear ocupied registers
    def clear_regs(self):
        self._xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        self._general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
        self._general64 = ['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax']

    def add_asm_function(self, label, code):
        #TODO --- code can also be callable
        self._asm_functions[label] = code

    def save_regs(self, regs):
        return ''.join(self._save_reg(reg) for reg in regs)

    def load_regs(self, regs):
        return ''.join(self._load_reg(reg) for reg in regs)

    def _save_reg(self, reg):
        name = '%s_%i' % (reg, id(self))
        if self.regs.is_xmm(reg):
            ds_reg = "float %s[4]\n" % name
            if proc.AVX:
                code = "vmovaps oword [%s], %s\n" % (name, reg)
            else:
                code = "movaps oword [%s], %s\n" % (name, reg)
        elif self.regs.is_reg32(reg):
            ds_reg = "uint32 %s\n" % name
            code = "mov dword [%s], %s\n" % (name, reg)
        elif self.regs.is_reg64(reg):
            ds_reg = "uint64 %s\n" % name
            code = "mov qword [%s], %s\n" % (name, reg)
        else:
            raise ValueError("Unknown register. Cannot be saved.", reg)
        self._saved_regs.add(ds_reg)
        return code

    def _load_reg(self, reg):
        name = '%s_%i' % (reg, id(self))
        if self.regs.is_xmm(reg):
            if proc.AVX:
                code = "vmovaps %s, oword [%s]\n" % (reg, name) 
            else:
                code = "movaps %s, oword [%s]\n" % (reg, name)
        elif self.regs.is_reg32(reg):
            code = "mov %s, dword [%s]\n" % (reg, name)
        elif self.regs.is_reg64(reg):
            code = "mov %s, qword [%s]\n" % (reg, name)
        return code

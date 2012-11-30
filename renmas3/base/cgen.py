import platform
import inspect
import renmas3.switch as proc

from .arg import create_argument, Struct, Integer, Float, Vec3, UserType, Attribute
from .arg import Integer, Vec3I, Pointer, StructPtr, Name, Const, Subscript
from .arg import Callable, create_user_type
from .shader import Shader
from .vector3 import Vector3
from .instr import load_struct_ptr, load_operand

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
    else:
        if inspect.isclass(typ):
            if hasattr(typ, 'user_type'):
                typ_name, fields = typ.user_type()
                usr_type = create_user_type(typ_name, fields)
                if usr_type.typ in _user_types:
                    pass #TODO -- check if two types are compatabile
                else:
                    _user_types[usr_type.typ] = usr_type
            else:
                raise ValueError("Class does not have user_type metod defined", typ)
        else:
            raise ValueError("Type is not class", typ)

def _copy_from_regs(args):
    xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    bits = platform.architecture()[0]
    for a in args:
        if isinstance(a, Integer):
            code += "mov dword [%s], %s \n" % (a.name, general.pop())
        elif isinstance(a, Float):
            code += "movss dword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, Vec3):
            code += "movaps oword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, StructPtr):
            if bits == '64bit':
                reg = general.pop()
                reg = 'r' + reg[1:]
                code += "mov qword [%s], %s \n" % (a.name, reg)
            else:
                code += "mov dword [%s], %s \n" % (a.name, general.pop())
        else:
            raise ValueError('Unknown argument', a)
    return code

def _copy_to_regs(cgen, operands, input_args):
    if len(operands) != len(input_args):
        raise ValueError("Argument length mismatch", operands, input_args)

    bits = platform.architecture()[0]
    xmm = ['xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['esi', 'edx', 'ecx', 'ebx', 'eax']
    ptr_reg = 'rbp' if bits == '64bit' else 'ebp'
    reg2 = 'edi'
    tmp_xmm = 'xmm7'
    cgen.register(reg=ptr_reg)
    cgen.register(reg=reg2)

    code = ''
    for operand, arg in zip(operands, input_args):
        if isinstance(arg, Integer):
            reg = general.pop()
            cgen.register(reg=reg)
            co, reg, typ = load_operand(cgen, operand, dest_reg=reg, ptr_reg=ptr_reg)
            code += co
            if typ != Integer:
                raise ValueError("Type mismatch when passing parameter to function", arg, typ)
        elif isinstance(arg, Float) or isinstance(arg, Vec3):
            reg = xmm.pop()
            co, reg, typ = load_operand(cgen, operand, dest_reg=reg, ptr_reg=ptr_reg)
            code += co
            if typ != type(arg):
                raise ValueError("Type mismatch when passing parameter to function", arg, typ)
        elif isinstance(arg, StructPtr):
            reg = general.pop()
            if bits == '64bit':
                reg = 'r' + reg[1:]
            arg = cgen.get_arg(operand)
            if isinstance(arg, Struct):
                code, dummy, dummy = load_struct_ptr(cgen, operand, reg)
            else:
                raise ValueError("User type argument is expected.", src)
        else:
            raise ValueError("Unsuported argument type!", operand, arg)
    return code

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
        return None

class Reference:
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj
        self._counter = 0

class _Locals:
    def __init__(self):
        self._free_args = {}
        self._used_args = {}

    def gen_name(self):
        name = "local" + str(id(self)) + str(self._counter)
        self._counter += 1
        return name

    def create_arg(self, name, arg_type):
        pass
        # 1. unbind name if it exist
        # 2. try find free arg of specified type
        # 3. if arg is not find create new arg
        # 4. bind name to new argument

    def get_arg(self, name):
        for key, value in self._used_args.items():
            pass
        return None

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
        self._asm_functions = []
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
            code = _copy_to_regs(self, obj.args, shader.input_args)
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
        for typ_name, typ in _user_types.items():
            data += typ.generate_struct()

        for arg in self._input_args:
            data += arg.generate_data()

        for name, arg in iter(self._args):
            data += arg.generate_data()

        for arg in self._locals.values():
            data += arg.generate_data()

        for arg in self._constants.values():
            data += arg.generate_data()

        for ds_reg in self._saved_regs:
            data += ds_reg

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
        #print (code)
        shader = Shader(self._name, code, self._args, self._input_args,
                self._shaders, self._ret_type, self._func,
                functions=self._asm_functions)
        return shader

    #create const it it's doesnt exist
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
        if path is not None:
            if isinstance(arg, Struct):
                full_path = name + '.' + path
                arg = arg.get_argument(full_path)
        return arg

    def _create_arg_from_callable(self, src, obj):
        arg = self.get_arg(src)
        if arg is not None and isinstance(arg, Struct):
            if arg.typ.typ != obj.name:
                raise ValueError("Type mismatch", arg.typ.typ, obj.name)
            return arg
        if obj.name not in _user_types:
            raise ValueError("Unregistered type %s is not registerd." % obj.name)

        arg = Struct(src, _user_types[obj.name])
        self._locals[src] = arg
        return arg


    def create_arg(self, dest, value=None, typ=None):
        if isinstance(dest, Name):
            dest = dest.name
        if isinstance(value, Callable):
            return self._create_arg_from_callable(dest, value)
        arg = self.get_arg(dest)
        if arg is not None:
            return arg
        if isinstance(dest, Attribute):
            raise ValueError("Cannot create loacl argument for attribut!")

        if isinstance(value, str): # a = b --- create argument a that have same type as b
            arg2 = self.get_arg(value)
            if isinstance(arg2, Struct):
                arg = create_argument(dest, value=arg2.typ)
            else:
                arg = create_argument(dest, typ=type(arg2))
        else:
            arg = create_argument(dest, value=value, typ=typ)
        if isinstance(arg, Struct): #automatic registration!!!! think TODO
            if arg.typ.typ not in _user_types:
                raise ValueError("User type %s is not registerd." % arg.typ.typ)
        self._locals[dest] = arg
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

    def add_asm_function(self, label, code):
        #TODO --- code can also be callable
        self._asm_functions.append((label, code))

    def save_regs(self, regs):
        code = ''
        for reg in regs:
            code += self._save_reg(reg)
        return code

    def load_regs(self, regs):
        code = ''
        for reg in regs:
            code += self._load_reg(reg)
        return code

    def _save_reg(self, reg):
        #TODO make class that hold all regs and implement many usufel functions like is_xmm, is general32, etc...
        xmms = ('xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0')
        general32 = ('ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax')
        general64 = ('rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax')
        name = '%s_%i' % (reg, id(self))
        if reg in xmms:
            ds_reg = "float %s[4]\n" % name
            if proc.AVX:
                code = "vmovaps oword [%s], %s\n" % (name, reg)
            else:
                code = "movaps oword [%s], %s\n" % (name, reg)
        elif reg in general32:
            ds_reg = "uint32 %s\n" % name
            code = "mov dword [%s], %s\n" % (name, reg)
        elif reg in general64:
            ds_reg = "uint64 %s\n" % name
            code = "mov qword [%s], %s\n" % (name, reg)
        else:
            raise ValueError("Unknown register. Cannot be saved.", reg)
        self._saved_regs.add(ds_reg)
        return code

    def _load_reg(self, reg):
        xmms = ('xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0')
        general32 = ('ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax')
        general64 = ('rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax')
        name = '%s_%i' % (reg, id(self))
        if reg in xmms:
            if proc.AVX:
                code = "vmovaps %s, oword [%s]\n" % (reg, name) 
            else:
                code = "movaps %s, oword [%s]\n" % (reg, name)
        elif reg in general32:
            code = "mov %s, dword [%s]\n" % (reg, name)
        elif reg in general64:
            code = "mov %s, qword [%s]\n" % (reg, name)
        return code

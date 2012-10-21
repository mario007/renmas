import platform
from .arg import create_argument, Struct, Integer, Float, Vec3, UserType, Attribute
from .arg import Integer, Vec3I, Pointer, StructPtr
from .arg import Callable
from .shader import Shader
from ..core import Vector3
from .instr import load_int_into_reg, load_float_into_reg, load_vec3_into_reg
from .instr import load_struct_ptr

_user_types = {}
_built_in_functions = {}

def register_function(name, func, inline=False):
    _built_in_functions[name] = (func, inline)

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

def _load_and_check_int(cgen, reg, src, ptr_reg):
    if isinstance(src, int):
        code = "mov %s, %i\n" % (reg, src)
    elif isinstance(src, str) or isinstance(src, Attribute):
        arg = cgen.get_arg(src)
        if not isinstance(arg, Integer):
            raise ValueError("Int argument is expected!", arg, src)
        code = load_int_into_reg(cgen, reg, src, ptr_reg)
    else:
        raise ValueError("Unsuported argument to shader or function", src)
    return code

def _load_and_check_float(cgen, reg, src, ptr_reg, reg2):
    if isinstance(src, int) or isinstance(src, float):
        src = float(src)
        arg = cgen.create_const(src)
        code = load_float_into_reg(cgen, reg, arg.name, ptr_reg)
    elif isinstance(src, str) or isinstance(src, Attribute):
        arg = cgen.get_arg(src)
        if isinstance(arg, Integer):
            code = load_int_into_reg(cgen, reg2, src, ptr_reg)
            code += convert_int_to_float(reg2, reg)
        elif isinstance(arg, Float):
            code = load_float_into_reg(cgen, reg, src, ptr_reg)
        else:
            raise ValueError('Float argument is expected.')
        pass
    else:
        raise ValueError("Unsuported argument to shader or function", src)
    return code

def _load_and_check_vec3(cgen, reg, src, ptr_reg):
    if isinstance(src, str) or isinstance(src, Attribute):
        arg = cgen.get_arg(src)
        if isinstance(arg, Vec3):
            code = load_vec3_into_reg(cgen, reg, src, ptr_reg)
        else:
            raise ValueError("Vector3 argument is expected.", src)
    else:
        raise ValueError("Unsuported argument to shader or function", src)
    return code

def _load_and_check_struct(cgen, reg, src):
    if isinstance(src, str) or isinstance(src, Attribute):
        arg = cgen.get_arg(src)
        if isinstance(arg, Struct):
            code, dummy, dummy = load_struct_ptr(cgen, src, reg)
        else:
            raise ValueError("User type argument is expected.", src)
    else:
        raise ValueError("Unsuported argument to shader or function", src)
    return code

def _copy_to_regs(cgen, operands, input_args):
    if len(operands) != len(input_args):
        raise ValueError("Argument length mismatch", operands, input_args)

    bits = platform.architecture()[0]
    xmm = ['xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['esi', 'edx', 'ecx', 'ebx', 'eax']
    if bits == '64bit':
        ptr_reg = 'rbp'
    else:
        ptr_reg = 'ebp'
    reg2 = 'edi'
    tmp_xmm = 'xmm7'

    code = ''
    for operand, arg in zip(operands, input_args):
        if isinstance(arg, Integer):
            reg = general.pop()
            code += _load_and_check_int(cgen, reg, operand, ptr_reg)
        elif isinstance(arg, Float):
            reg = xmm.pop()
            code += _load_and_check_float(cgen, reg, operand, ptr_reg, reg2)
        elif isinstance(arg, Vec3):
            reg = xmm.pop()
            code += _load_and_check_vec3(cgen, reg, operand, ptr_reg)
        elif isinstance(arg, StructPtr):
            reg = general.pop()
            if bits == '64bit':
                reg = 'r' + reg[1:]
            code += _load_and_check_struct(cgen, reg, operand)
        else:
            raise ValueError("Unsuported argument type!", operand, arg)
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
                return _built_in_functions[obj.name][2]
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
            code += "call %s\n" % obj.name
            typ = shader.ret_type
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

    def create_temp(self, typ):
        pass

    def release_temp(self, temp):
        pass

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


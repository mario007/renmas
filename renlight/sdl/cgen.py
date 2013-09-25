"""
    This module holds implementation of code generator that
    convert list of statements in assembly code.
"""

import platform

import renlight.proc as proc
from .utils import LocalArgs, Registers
from .strs import Attribute, Callable, Const, Name, Subscript
from .args import Argument, arg_from_value, _struct_desc,\
    StructArg, IntArg, Vec2Arg, Vec3Arg, Vec4Arg, FloatArg
from .asm_cmds import store_func_args, load_func_args, move_reg_to_reg,\
    move_reg_to_mem, move_mem_to_reg


class CodeGenerator:
    def __init__(self):
        self.regs = Registers()
        self._counter = 0

    @property
    def AVX(self):
        return proc.AVX

    @property
    def BIT64(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            return True
        return False

    def get_arg(self, src):
        arg = None
        if isinstance(src, (Attribute, Name, Subscript)):
            name = src.name
        else:
            raise ValueError("Unsuported source type for argument")
        if name in self._locals:
            arg = self._locals[name]
        if name in self._args:
            arg = self._args[name]
        for a in self._func_args:
            if name == a.name:
                arg = a
                break
        return arg

    def _is_arg_fixed(self, src):
        arg = self.get_arg(src)
        if arg is None:
            return False
        if isinstance(src, Attribute):
            return True
        elif isinstance(src, Subscript):
            return True
        else:
            return False

    def is_user_type(self, src):
        if not isinstance(src, Callable):
            raise ValueError("User types must be callable!", src)
        return src.name in _struct_desc

    def create_arg(self, dest, value):
        if not isinstance(value, (Const, Name,
                                  Attribute, Subscript, Callable))\
                and not issubclass(value, Argument):
            raise ValueError("Unknown(unsuported) value in create arg!", value)

        arg = self.get_arg(dest)
        if isinstance(value, Const):
            name = self._generate_name('local')
            arg2 = arg_from_value(name, value.const)
        elif isinstance(value, Callable):
            name = self._generate_name('local')
            struct_desc = _struct_desc[value.name]
            val = struct_desc.factory()
            arg2 = StructArg(name, val)
        elif issubclass(value, Argument):  # value is Argument class
            arg2 = value(self._generate_name('local'))
        else:
            arg2 = self.get_arg(value)
            if arg2 is None:
                raise ValueError("Argument doesn't exist!", value)
        if isinstance(arg, StructArg):
            arg = arg.resolve(dest.path)
        if type(arg) != type(arg2) and self._is_arg_fixed(dest):
            raise ValueError("Argument is fixed and cannot change type!")
        if type(arg) == type(arg2):
            return arg
        else:
            if isinstance(dest, (Attribute, Subscript)):
                raise ValueError("Canot create attribute or subscirpt\
                        as local arguments.")
            arg3 = self._locals.add(dest.name, arg2)
            return arg3

    def _struct_def(self, struct_arg, structs):
        for arg in struct_arg.args:
            if isinstance(arg, StructArg):
                return self._struct_def(arg, structs)
        if type(struct_arg.value) in structs:
            return ''
        structs.add(type(struct_arg.value))
        data = struct_arg.struct_def(self)
        return data

    def _generate_data_section(self, args, func_args):
        # First we collect all diferent structure types in our program
        all_args = list(args) + list(func_args) + list(self._locals.get_args())
        data = ''
        structs = set()
        for arg in all_args:
            if isinstance(arg, StructArg):
                data += self._struct_def(arg, structs)

        #specs = self._tmp_specs + self._tmp_specs_used
        #for arg in specs:
        #    data += arg.generate_data()

        for arg in all_args:
            data += arg.generate_data(self)

        for arg in self._constants.values():
            data += arg.generate_data(self)

        for ds_reg in self._saved_regs:
            data += ds_reg

        return data

    def generate_code(self, statements, args=[], is_func=False,
                      name=None, func_args=[], shaders=[]):

        self._locals = LocalArgs()
        self._constants = {}
        self._ret_type = None
        self._saved_regs = set()
        self._shaders = shaders

        self._args = {}
        for a in args:
            self._args[a.name] = a
        self._func_args = func_args

        code = ''.join(self.inst_code(s) for s in statements)
        data = self._generate_data_section(args, func_args) + '\n'
        data = "\n#DATA \n" + data + "#CODE \n"
        glo = ''
        if is_func:
            if name is None:
                raise ValueError("Function shaders must have a name!")
            glo = "global %s:\n" % name
        code = glo + store_func_args(self, func_args) + code
        if is_func:
            code = data + code + 'ret\n'
        else:
            code = data + code + '#END \n'

        return code, self._ret_type

    def inst_code(self, stm):
        """
            Generate code for statement.
            @param - statement
        """
        self.clear_regs()
        #self._free_tmp_specs()
        return stm.asm_code(self)

    def clear_regs(self):
        """
            Free all registers.
        """
        self._xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4',
                     'xmm3', 'xmm2', 'xmm1', 'xmm0']
        self._general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
        self._general64 = ['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax']

    def register(self, typ=None, bit=32, reg=None):
        """
            Allocate currently unused register for temporally usage.
            @param typ - reigster type(general, pointer or xmm)
            @param bit - 32 or 64
            @param reg - directly specified register that is needed
        """
        assert typ is not None or reg is not None
        if typ == 'pointer':
            typ = 'general'
            bit = 64 if self.BIT64 else 32
        if reg is not None and reg in self._xmm:
            self._xmm.remove(reg)
            return reg
        if reg is not None:
            if reg in self._general:
                self._general.remove(reg)
                self._general64.remove('r' + reg[1:])
                return reg
            if reg in self._general64:
                self._general64.remove(reg)
                self._general.remove('e' + reg[1:])
                return reg

        if reg is not None:
            raise ValueError("Register %s is allready ocupied!" % reg)

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
        """
            Free currently used register.
            @param reg - Register that must be freed
        """
        if self.regs.is_xmm(reg) and reg not in self._xmm:
            self._xmm.append(reg)
        elif self.regs.is_reg32(reg) and reg not in self._general:
            self._general.append(reg)
            self._general64.append('r' + reg[1:])
        elif self.regs.is_reg64(reg) and reg not in self._general64:
            self._general64.append(reg)
            self._general.append('e' + reg[1:])
        else:
            raise ValueError("This register was allready unused!!!")

    def _generate_name(self, prefix=''):
        """
            Used for generating names of local variables and constants.
            @param prefix - Prefix of generated name
        """
        name = prefix + '_' + str(self._counter) + str(id(self))
        self._counter += 1
        return name

    def _get_shader(self, name):
        for shader in self._shaders:
            if name == shader.name:
                return shader
        return None

    def _get_function(self, name):
        return None

    def _find_free_reg(self, regs, typ):
        acum = self.acum_for_type(typ)
        xmm = ('xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7')
        g32 = ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp')
        g64 = ('rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp')

        reg = None
        if self.regs.is_xmm(acum):
            f = xmm
        elif self.regs.is_reg32(acum):
            f = g32
        elif self.regs.is_reg64(acum):
            f = g64
        for r in f:
            if r not in regs:
                reg = r
                break

        if reg is None:
            raise ValueError("Could not find free register for acumulator!")
        return reg

    def acum_for_type(self, arg_type):
        types = {IntArg: 'eax', FloatArg: 'xmm0',
                 Vec2Arg: 'xmm0', Vec3Arg: 'xmm0', Vec4Arg: 'xmm0'}
        return types[arg_type]

    def generate_callable(self, obj, regs):
        if not isinstance(obj, Callable):
            raise ValueError("Callable is expected!", obj)

        shader = self._get_shader(obj.name)
        if shader is not None:
            code = self.save_regs(regs)
            self.clear_regs()
            code += load_func_args(self, obj.args, shader.func_args)
            self.clear_regs()
            code += "call %s\n" % obj.name
            typ = shader.ret_type
            if typ is None:
                typ = IntArg
                reg = self.acum_for_type(typ)
                self.register(reg=reg)
            else:
                reg = self._find_free_reg(regs, typ)
                acum = self.acum_for_type(typ)
                code += move_reg_to_reg(self, acum, reg)
                self.register(reg=reg)
            for r in regs:
                if r != reg:
                    self.register(reg=r)
            code += self.load_regs(regs)
            return code, reg, typ

        # function = self.get_function(obj.name)
        # if function is not None:
        #     func, inline = function
        #     if not inline:
        #         self.clear_regs()
        #     code, reg, typ = func(self, obj.args)
        #     if not inline:
        #         self.clear_regs()
        #         self.register(reg=reg)
        #     return code, reg, typ

        raise ValueError("Callable %s doesn't exist." % obj.name)

    def save_regs(self, regs):
        code = ''
        for reg in regs:
            name = '%s_%i' % (reg, id(self))
            if self.regs.is_xmm(reg):
                ds_reg = "float %s[4]\n" % name
            elif self.regs.is_reg32(reg):
                ds_reg = "uint32 %s\n" % name
            elif self.regs.is_reg64(reg):
                ds_reg = "uint64 %s\n" % name

            self._saved_regs.add(ds_reg)
            code += move_reg_to_mem(self, reg, name)
        return code

    def load_regs(self, regs):
        code = ''
        for reg in regs:
            name = '%s_%i' % (reg, id(self))
            code += move_mem_to_reg(self, reg, name)
        return code

    def register_ret_type(self, typ):
        if self._ret_type is None:
            self._ret_type = typ
        if self._ret_type != typ:
            raise ValueError("Return Type mismatch ", self._ret_type, typ)

    def create_const(self, operand):
        if not isinstance(operand, Const):
            raise ValueError("Const is expected!", operand)

        name = self._generate_name('const')
        arg = arg_from_value(name, operand.const)
        key = (type(arg), operand.const)
        if key in self._constants:
            return self._constants[key]
        self._constants[key] = arg
        return arg

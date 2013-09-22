"""
    This module holds implementation of code generator that
    convert list of statements in assembly code.
"""

import platform
import renlight.proc as proc
from .utils import LocalArgs, Registers
from .strs import Attribute, Callable, Const, Name, Subscript
from .args import Argument, arg_from_value


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

    def create_arg(self, dest, value):
        arg = self.get_arg(dest)
        if isinstance(value, (Const, Name, Attribute, Subscript)) or issubclass(value, Argument):
            if isinstance(value, Const):
                arg2 = arg_from_value(self._generate_name('local'), value.const)
            elif issubclass(value, Argument):#Note value is Argument class IntArg, etc...
                arg2 = value(self._generate_name('local'))
            else:
                arg2 = self.get_arg(value)
                if arg2 is None:
                    raise ValueError("Argument doesn't exist!", value)
            if type(arg) != type(arg2) and self._is_arg_fixed(dest):
                raise ValueError("This argument is fixed and cannot change type!")
            if type(arg) == type(arg2):
                return arg
            else:
                if isinstance(dest, (Attribute, Subscript)):
                    raise ValueError("Canot create attribute or subscirpt as local arguments.")
                arg3 = self._locals.add(dest.name, arg2)
                return arg3

        elif isinstance(value, Callable):
            raise ValueError("Implement this user type(callable) HitPoint()")
        else:
            raise ValueError("Unknown value in create arg! ", value)

    def _generate_data_section(self, args, func_args):
        data = ''
        #TODO remove duplicates, struct inside sturct
        #data += self._generate_struct_defs()

        #specs = self._tmp_specs + self._tmp_specs_used
        #for arg in specs:
        #    data += arg.generate_data()

        for arg in func_args:
            data += arg.generate_data(self)

        for arg in args:
            data += arg.generate_data(self)

        args = self._locals.get_args()
        for arg in args:
            data += arg.generate_data(self)

        for arg in self._constants.values():
            data += arg.generate_data(self)

        #for ds_reg in self._saved_regs:
        #    data += ds_reg

        return data

    def generate_code(self, statements, args=[], is_func=False, name=None, func_args=[]):

        self._locals = LocalArgs()
        self._constants = {}
        self._ret_type = None
        self._saved_regs = set()

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
                raise ValueError("If shader is function it must also have a name!")
            glo = "global %s:\n" % name
        #code = glo + store_func_args(self, func_args) + code #NOTE fix this quickly
        if is_func:
            code = data + code + 'ret\n'
        else:
            code = data + code + '#END \n'

        return code

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
        self._xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
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
            Used for generating names for local variables and name of constants.
            @param prefix - Prefix of generated name
        """
        name = prefix + '_' + str(self._counter) + str(id(self))
        self._counter += 1
        return name


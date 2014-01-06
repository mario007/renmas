"""
    Utilities classes.
"""
import struct
from .args import StructArg


class Registers:
    def __init__(self):
        self._xmm = ('xmm7', 'xmm6', 'xmm5', 'xmm4',
                     'xmm3', 'xmm2', 'xmm1', 'xmm0')
        self._general32 = ('ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax')
        self._general64 = ('rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax')

    def is_xmm(self, reg):
        return reg in self._xmm

    def is_reg32(self, reg):
        return reg in self._general32

    def is_reg64(self, reg):
        return reg in self._general64

    def is_general(self, reg):
        return reg in self._general32 or reg in self._general64

    def type(self, reg):
        if reg in self._xmm:
            return 'xmm'
        if reg in self._general32 or reg in self._general64:
            return 'general'
        raise ValueError("Unknown register!", reg)


class LocalArgs:
    def __init__(self):
        self._free_args = {}
        self._used_args = {}

    def _move_to_free_args(self, arg):
        if type(arg) not in self._free_args:
            self._free_args[type(arg)] = set()
        self._free_args[type(arg)].add(arg)

    def _get_free_arg(self, arg):
        arg_type = type(arg)
        typ1 = type(arg.value)
        if arg_type in self._free_args:
            try:
                if isinstance(arg, StructArg):
                    for a in self._free_args[arg_type]:
                        if isinstance(a.value, typ1):
                            self._free_args[arg_type].remove(a)
                            return a
                else:
                    return self._free_args[arg_type].pop()
            except KeyError:
                return None
        return None

    def get_arg(self, name):
        if name in self._used_args:
            return self._used_args[name]
        return None

    def get_args(self):
        args = list(self._used_args.values())
        for key, val in self._free_args.items():
            args = args + list(val)
        return args

    def add(self, name, arg):
        loc_arg = self.get_arg(name)
        if loc_arg is not None and type(loc_arg) == type(arg):
            if isinstance(loc_arg, StructArg) and isinstance(arg, StructArg):
                typ1, typ2 = type(loc_arg.value), type(arg.value)
                if typ1 is typ2:
                    return loc_arg
            else:
                return loc_arg

        if loc_arg is not None:
            self._move_to_free_args(loc_arg)

        loc_arg = self._get_free_arg(arg)
        if loc_arg is None:
            loc_arg = arg

        self._used_args[name] = loc_arg
        return loc_arg

    def __contains__(self, name):
        return name in self._used_args

    def __getitem__(self, name):
        return self._used_args[name]


def float2hex(f):
    r = struct.pack('f', f)
    r1 = struct.unpack('I', r)[0]
    return hex(r1)


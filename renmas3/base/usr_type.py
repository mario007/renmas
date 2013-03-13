
import platform
from .arg import Argument, check_ptr_reg

class UserType:
    def __init__(self, typ):
        self._typ = typ
        self._args_lst = []
        self._args = {}

    @property
    def typ(self):
        return self._typ

    def add(self, arg):
        if arg.name in self._args:
            raise ValueError("Argument allready exist!", arg)
        self._args[arg.name] = arg
        self._args_lst.append(arg)

    def generate_paths(self, name):
        paths = {}
        for arg in self._args_lst:
            if isinstance(arg, Struct):
                #TODO not tested yet - struct inside struct
                for key, value in arg.paths.items():
                    paths[name + '.' + key] = value
            else:
                paths[name + '.' + arg.name] = arg
        return paths

    def generate_struct(self):
        code = "struct %s \n" % self._typ
        for a in self._args_lst:
            code += a.generate_data()
        code += "end struct \n\n"
        return code

class Struct(Argument):
    def __init__(self, name, typ):
        super(Struct, self).__init__(name)
        self._typ = typ
        self._paths = typ.generate_paths(name)

    @property
    def typ(self):
        return self._typ

    @property
    def paths(self):
        return self._paths

    def argument_exist(self, path): # path example: path = ps.x.y
        return path in self._paths

    def get_argument(self, path):
        if path in self._paths:
            return self._paths[path]
        return None

    def generate_data(self):
        return '%s %s\n' % (self._typ.typ, self.name)

    def set_value(self, ds, value, path, idx_thread=None):
        for p, arg in self._paths.items():
            obj = getattr(value, arg.name)
            if obj is None:
                continue
            arg.set_value(ds, obj, p, idx_thread)

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        check_ptr_reg(cgen, dest_reg)
        code = "mov %s, %s \n" % (dest_reg, self.name)
        return code, dest_reg, Struct

    def load_attr_cmd(self, cgen, path, dest_reg=None, ptr_reg=None):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen, ptr_reg)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2, src_reg2, type2 = arg.load_attr(cgen, asm_path, src_reg, dest_reg)
        if ptr_reg is None:
            cgen.release_reg(src_reg)

        return code1 + code2, src_reg2, type2 

    def load_attr_subscript_cmd(self, cgen, path, index, dest_reg=None, ptr_reg=None):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen, ptr_reg)
        asm_path = "%s.%s" %(self.typ.typ, path)
        code2, src_reg2, type2 = arg.load_subscript_attr(cgen, asm_path, index, src_reg, dest_reg)
        if ptr_reg is None:
            cgen.release_reg(src_reg)

        return code1 + code2, src_reg2, type2 

    def store_attr_subscript_cmd(self, cgen, path, reg, typ, index):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2 = arg.store_subscript_attr(cgen, asm_path, src_reg, reg, typ, index)
        cgen.release_reg(src_reg)
        return code1 + code2

    def store_attr_cmd(self, cgen, path, reg):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2 = arg.store_attr(cgen, asm_path, src_reg, reg)
        cgen.release_reg(src_reg)
        return code1 + code2

    def store_attr_const(self, cgen, path, const):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2 = arg.store_attr_const(cgen, asm_path, src_reg, const)

        cgen.release_reg(src_reg)
        return code1 + code2

    @classmethod
    def register_type(cls):
        return 'pointer'

class StructPtr(Struct):
    def generate_data(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            return 'uint64 %s\n' % self.name
        else:
            return 'uint32 %s\n' % self.name

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        check_ptr_reg(cgen, dest_reg)
        if cgen.BIT64:
            code = "mov %s, qword [%s] \n" % (dest_reg, self.name)
        else:
            code = "mov %s, dword [%s] \n" % (dest_reg, self.name)
        return code, dest_reg, StructPtr

    def store_cmd(self, cgen, reg):
        check_ptr_reg(cgen, reg)
        if cgen.BIT64:
            code = "mov qword [%s], %s \n" % (self.name, reg)
        else:
            code = "mov dword [%s], %s \n" % (self.name, reg)
        return code

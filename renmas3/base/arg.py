import platform
import inspect
from .vector3 import Vector3

def conv_int_to_float(cgen, reg, xmm):
    if cgen.AVX:
        return "vcvtsi2ss %s, %s, %s \n" % (xmm, xmm, reg)
    else:
        return "cvtsi2ss %s, %s \n" % (xmm, reg)

def conv_float_to_int(cgen, reg, xmm):
    if cgen.AVX:
        return "vcvttss2si %s, %s \n" % (reg, xmm)
    else:
        return "cvttss2si %s, %s \n" % (reg, xmm)

class Argument:
    def __init__(self, name):
        self.name = name

    @staticmethod
    def set_value(ds, value, path, idx_thread=None):
        raise NotImplementedError()

    @staticmethod
    def get_value(ds, path, idx_thread=None):
        raise NotImplementedError()

    def generate_data(self):
        raise NotImplementedError()

class Integer(Argument):

    def __init__(self, name, value=0):
        super(Integer, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = int(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @staticmethod
    def set_value(ds, value, path, idx_thread=None):
        if idx_thread is None:
            for d in ds:
                d[path] = value 
        else:
            ds[idx_thread][path] = value

    @staticmethod
    def get_value(ds, path, idx_thread=None):
        if idx_thread is None:
            return ds[0][path]
        else:
            return ds[idx_thread][path]

    def generate_data(self):
        return 'int32 %s = %i \n' % (self.name, self._value) 

    @staticmethod
    def load_cmd(cgen, name, dest_reg=None, path=None, ptr_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='general')
        #TODO pointer register check 32 or 64 bit
        
        tmp = dest_reg
        if cgen.regs.is_xmm(dest_reg):
            tmp = cgen.register(typ='general')
        if path is None:
            code = "mov %s, dword [%s] \n" % (tmp, name)
        else:
            if ptr_reg is None:
                raise ValueError("If Integer is attribute register pointer is also required")
            code = "mov %s, dword [%s + %s]\n" % (tmp, ptr_reg, path)

        if cgen.regs.is_xmm(dest_reg): #implicit conversion to float
            conversion = conv_int_to_float(cgen, tmp, dest_reg)
            cgen.release_reg(tmp)
            return code + conversion, dest_reg, Float
        else:
            return code, tmp, Integer

    @staticmethod
    def store_cmd(cgen, reg, name, path=None, ptr_reg=None):
        if path is None:
            code = "mov dword [%s], %s \n" % (name, reg)
        else:
            if ptr_reg is None:
                raise ValueError("If Integer is attribute register pointer is also required")
            code = "mov dword [%s + %s], %s\n" % (ptr_reg, path, reg)
        return code

    @staticmethod
    def neg_cmd(cgen, reg):
        return 'neg %s\n' % reg

    @staticmethod
    def supported(operator, typ):
        if typ != Integer:
            return False
        if operator not in ('+', '-', '/', '*', '%'):
            return False
        return True

    @staticmethod
    def arith_cmd(cgen, reg1, reg2, typ2, operator):
        if typ2 != Integer:
            raise ValueError('Wrong type for integer arithmetic', typ2)
        if operator == '+':
            code = 'add %s, %s\n' % (reg1, reg2)
        elif operator == '-':
            code = 'sub %s, %s\n' % (reg1, reg2)
        elif operator == '%' or operator == '/': #TODO test 64-bit implementation is needed
            code, reg1 = Integer._arith_div(cgen, reg1, reg2, operator)
        elif operator == '*':
            code = "imul %s, %s\n" % (reg1, reg2)
        else:
            raise ValueError("Unsuported operator", operator)
        return code, reg1, Integer

    @staticmethod
    def _arith_div(cgen, reg1, reg2, operator):
        epilog = """
        push eax
        push edx
        push esi
        """
        line1 = "mov eax, %s\n" % reg1
        line2 = "mov esi, %s\n" % reg2
        line3 = "xor edx, edx\n"
        line4 = "idiv esi\n"
        line5 = "pop esi\n"
        if operator == '/':
            line6 = "pop edx\n"
            line7 = "mov %s, eax\n" % reg1
            if reg1 == 'eax':
                line8 = "add esp, 4\n"
            else:
                line8 = "pop eax\n"
        else:
            line6 = "mov %s, edx\n" % reg1
            if reg1 == 'edx':
                line7 = "add esp, 4\n"
            else:
                line7 = "pop edx\n"
            if reg1 == 'eax':
                line8 = "add esp, 4\n"
            else:
                line8 = "pop eax\n"
        code = epilog + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
        return code, reg1


class Float(Argument):

    def __init__(self, name, value=0.0):
        super(Float, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = float(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @staticmethod
    def set_value(ds, value, path, idx_thread=None):
        if idx_thread is None:
            for d in ds:
                d[path] = value 
        else:
            ds[idx_thread][path] = value

    @staticmethod
    def get_value(ds, path, idx_thread=None):
        if idx_thread is None:
            return ds[0][path]
        else:
            return ds[idx_thread][path]

    def generate_data(self):
        return 'float %s = %f \n' % (self.name, self._value)

    @staticmethod
    def load_cmd(cgen, name, dest_reg=None, path=None, ptr_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)
        #TODO pointer register check 32 or 64 bit
        if path is None:
            if cgen.AVX:
                code = "vmovss %s, dword [%s] \n" % (dest_reg, name)
            else:
                code = "movss %s, dword [%s] \n" % (dest_reg, name)
        else:
            if ptr_reg is None:
                raise ValueError("If Float is attribute register pointer is also required")
            if cgen.AVX:
                code = "vmovss %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
            else:
                code = "movss %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, Float 

    @staticmethod
    def store_cmd(cgen, xmm, name, path=None, ptr_reg=None):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!")

        if path is None:
            if cgen.AVX:
                code = "vmovss dword [%s], %s \n" % (name, xmm)
            else:
                code = "movss dword [%s], %s \n" % (name, xmm)
            return code

        if ptr_reg is None:
            raise ValueError("If Float is attribute register pointer is also required")

        if cgen.AVX:
            code = "vmovss dword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code = "movss dword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code

    @staticmethod
    def neg_cmd(cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)

        #TODO Vector4 const (-1.0, -1.0, -1.0, -1.0)
        arg = cgen.create_const((-1.0, -1.0, -1.0))
        if cgen.AVX:
            code = "vmulss %s, %s, dword[%s]\n" % (xmm, xmm, arg.name) 
        else:
            code = "mulss %s, dword[%s]\n" % (xmm, arg.name) 
        return code

    @staticmethod
    def supported(operator, typ):
        if typ != Integer and typ != Float:
            return False
        if operator not in ('+', '-', '/', '*'):
            return False
        return True

    @staticmethod
    def arith_cmd(cgen, reg1, reg2, typ2, operator):
        if typ2 != Integer and typ2 != Float:
            raise ValueError('Wrong type for float arithmetic', typ2)
        if not cgen.regs.is_xmm(reg1):
            raise ValueError('Destination register must be xmm register', reg1)

        code = ''
        xmm = reg2
        if typ2 == Integer:
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg2, xmm)
            cgen.release_reg(xmm)

        if operator == '+':
            if cgen.AVX:
                code += "vaddss %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "addss %s, %s \n" % (reg1, xmm)
        elif operator == '-':
            if cgen.AVX:
                code += "vsubss %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "subss %s, %s \n" % (reg1, xmm)
        elif operator == '/':
            if cgen.AVX:
                code += "vdivss %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "divss %s, %s \n" % (reg1, xmm)
        elif operator == '*':
            if cgen.AVX:
                code += "vmulss %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "mulss %s, %s \n" % (reg1, xmm)
        else:
            raise ValueError("Unsuported operator", operator)
        return code, reg1, Float

    @staticmethod
    def rev_arith_cmd(cgen, reg1, reg2, typ2, operator):
        if not cgen.regs.is_xmm(reg1):
            raise ValueError('Destination register must be xmm register', reg1)

        code = ''
        xmm = reg2
        if typ2 == Integer:
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg2, xmm)
            cgen.release_reg(xmm)

        code3, reg3, typ3 = Float.arith_cmd(cgen, xmm, reg1, Float, operator)
        return code + code3, reg3, typ3

class Vec3(Argument):

    def __init__(self, name, value=Vector3(0.0, 0.0, 0.0)):
        super(Vec3, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @staticmethod
    def set_value(ds, value, path, idx_thread=None):
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds() 
        else:
            ds[idx_thread][path] = value.to_ds()

    @staticmethod
    def get_value(ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector3(val[0], val[1], val[2])

    def generate_data(self):
        v = self._value
        return 'float %s[4] = %f,%f,%f,0.0 \n' % (self.name, v.x, v.y, v.z)

    @staticmethod
    def load_cmd(cgen, name, dest_reg=None, path=None, ptr_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!")
        #TODO pointer register check 32 or 64 bit
        if path is None:
            if cgen.AVX:
                code = "vmovaps %s, oword [%s] \n" % (dest_reg, name)
            else:
                code = "movaps %s, oword [%s] \n" % (dest_reg, name)
        else:
            if ptr_reg is None:
                raise ValueError("If vector is attribute register pointer is also required")
            if cgen.AVX:
                code = "vmovaps %s, oword [%s + %s]\n" % (dest_reg, ptr_reg, path)
            else:
                code = "movaps %s, oword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, Vec3 
            
    @staticmethod
    def store_cmd(cgen, xmm, name, path=None, ptr_reg=None):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!")
    
        if path is None:
            if cgen.AVX:
                code = "vmovaps oword [%s], %s \n" % (name, xmm)
            else:
                code = "movaps oword [%s], %s \n" % (name, xmm)
            return code

        if ptr_reg is None:
            raise ValueError("If Float is attribute register pointer is also required")

        if cgen.AVX:
            code = "vmovaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code = "movaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code

    @staticmethod
    def neg_cmd(cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)

        #TODO Vector4 const (-1.0, -1.0, -1.0, -1.0)
        arg = cgen.create_const((-1.0, -1.0, -1.0))
        if cgen.AVX:
            code = "vmulps %s, %s, oword[%s]\n" % (xmm, xmm, arg.name) 
        else:
            code = "mulps %s, oword[%s]\n" % (xmm, arg.name) 
        return code

    @staticmethod
    def supported(operator, typ):
        if operator == '*':
            if typ == Integer or typ == Float or typ == Vec3:
                return True
        if operator not in ('+', '-', '/', '*'):
            return False
        if typ != Vec3:
            return False
        return True

    @staticmethod
    def _conv(cgen, reg2, typ2, operator):
        code = ''
        xmm = reg2
        if typ2 == Integer and operator == '*':
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg2, xmm)
            cgen.release_reg(xmm)

        if typ2 == Float and operator == '*':
            if cgen.AVX: #vblends maybe is faster investigate TODO
                code += "vshufps %s, %s, %s, 0x00\n" % (xmm, xmm, xmm)
            else:
                code += "shufps %s, %s, 0x00\n" % (xmm, xmm)
        return code, xmm

    @staticmethod
    def arith_cmd(cgen, reg1, reg2, typ2, operator):
        if not cgen.regs.is_xmm(reg1):
            raise ValueError('Destination register must be xmm register', reg1)

        if operator != '*' and (typ2 == Integer or typ2 == Float):
            raise ValueError('Wrong type for vector arithmetic', typ2)

        code, xmm = Vec3._conv(cgen, reg2, typ2, operator)
        if operator == '+':
            if cgen.AVX:
                code += "vaddps %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "addps %s, %s \n" % (reg1, xmm)
        elif operator == '-':
            if cgen.AVX:
                code += "vsubps %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "subps %s, %s \n" % (reg1, xmm)
        elif operator == '/':
            if cgen.AVX:
                code += "vdivps %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "divps %s, %s \n" % (reg1, xmm)
        elif operator == '*':
            if cgen.AVX:
                code += "vmulps %s, %s, %s \n" % (reg1, reg1, xmm)
            else:
                code += "mulps %s, %s \n" % (reg1, xmm)
        else:
            raise ValueError("Unsuported operator", operator)

        return code, reg1, Vec3

    @staticmethod
    def rev_arith_cmd(cgen, reg1, reg2, typ2, operator):
        if not cgen.regs.is_xmm(reg1):
            raise ValueError('Destination register must be xmm register', reg1)

        code, xmm = Vec3._conv(cgen, reg2, typ2, operator)
        code3, reg3, typ3 = Vec3.arith_cmd(cgen, xmm, reg1, Vec3, operator)
        return code + code3, reg3, typ3


class Vec3I(Argument):

    def __init__(self, name, x, y, z):
        super(Vec3, self).__init__(name)
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    @staticmethod
    def set_value(ds, value, path, idx_thread=None):
        x, y, z = value
        if idx_thread is None:
            for d in ds:
                d[path] = (x, y, z, 0)
        else:
            ds[idx_thread][path] = (x, y, z, 0)

    @staticmethod
    def get_value(ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return val[0:3]

    def generate_data(self):
        return 'int32 %s[4] = %i,%i,%i,0\n' % (self.name, self.x, self.y, self.z)

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
                    self._paths[name + '.' + key] = value
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
            arg.set_value(ds, obj, p, idx_thread)

class StructPtr(Struct):
    def generate_data(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            return 'uint64 %s\n' % self.name
        else:
            return 'uint32 %s\n' % self.name


class Pointer(Argument):
    def __init__(self, name, typ=None, value=0):
        super(Pointer, self).__init__(name)
        self._typ = typ
        self._value = value

    @property
    def typ(self):
        return self._typ

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            return 'uint64 %s = %i \n' % (self.name, self._value) 
        else:
            return 'uint32 %s = %i \n' % (self.name, self._value) 

    @staticmethod
    def set_value(ds, value, path, idx_thread=None):
        if idx_thread is None:
            for d in ds:
                d[path] = value 
        else:
            ds[idx_thread][path] = value

    @staticmethod
    def get_value(ds, path, idx_thread=None):
        if idx_thread is None:
            return ds[0][path]
        else:
            return ds[idx_thread][path]

#TODO implement locking of map and list???-think
class ArgumentList:
    def __init__(self, args=[]):
        self._args = []
        for a in args:
            self._args.append(a)

    def __contains__(self, arg):
        return arg in self._args

    def __iter__(self):
        for a in self._args:
            yield a

    def __len__(self):
        return len(self._args)

class ArgumentMap:
    def __init__(self, args=[]):
        self._args = {}
        for a in args:
            if not isinstance(a, Argument):
                raise ValueError("Wrong argument type", a)
            self._args[a.name] = a

    def add(self, arg):
        if not isinstance(arg, Argument):
            raise ValueError("Wrong argument type", arg)

        if arg.name in self._args:
            raise ValueError("Argument %s allready exist", arg.name)
        self._args[arg.name] = arg

    def __contains__(self, name):
        return name in self._args

    def __getitem__(self, name):
        return self._args[name]

    def __iter__(self):
        for a in self._args.items():
            yield a

#TODO check if name is something other than string!!!
def create_argument(name, value=None, typ=None, input_arg=False):
    if value is None and typ is None:
        raise ValueError("Argument could not be created because type and value is missing")
    if typ is not None:
        if typ == Integer:
            if value is None:
                arg = Integer(name, 0)
            else:
                arg = Integer(name, int(value))
        elif typ == Float:
            if value is None:
                arg = Float(name, 0.0)
            else:
                arg = Float(name, float(value))
        elif typ == Vec3:
            if value is None:
                arg = Vec3(name, Vector3(0.0, 0.0, 0.0))
            else:
                if not isinstance(value, Vector3):
                    raise ValueError("Value for Vec3 is expected to be instance of Vector3")
                arg = Vec3(name, value)
        elif typ == Vec3I:
            if value is None:
                arg = Vec3I(name, 0, 0, 0)
            else:
                x, y, z = value
                arg = Vec3I(name, int(x), int(y), int(z))
        elif typ == Pointer: #pointer in typ = UserType
                arg = Pointer(name, typ=value)
        elif hasattr(typ, 'user_type'):
            typ_name, fields = typ.user_type()
            usr_type = create_user_type(typ_name, fields)
            if input_arg:
                arg = StructPtr(name, usr_type)
            else:
                arg = Struct(name, usr_type)
        else:
            raise ValueError("Unknown type of arugment", typ)
        return arg

    if isinstance(value, int):
        arg = Integer(name, value)
    elif isinstance(value, float):
        arg = Float(name, value)
    elif isinstance(value, tuple) or isinstance(value, list):
        if len(value) != 3:
            raise ValueError('Wrong length of tuple', value)
        arg = Vec3(name, Vector3(float(value[0]), float(value[1]), float(value[2])))
    elif isinstance(value, Vector3):
        arg = Vec3(name, value)
    elif isinstance(value, UserType):
        if input_arg:
            arg = StructPtr(name, value)
        else:
            arg = Struct(name, value)
    else:
        raise ValueError('Unknown value type', value)
    return arg

#a5 = create_user_type_(typ="point", fields=[('x', 55)])
def create_user_type(typ, fields):
    usr_type = UserType(typ)
    for n, v in fields:
        if inspect.isclass(v):
            arg = create_argument(n, typ=v)
        else:
            arg = create_argument(n, value=v)
        usr_type.add(arg)
    return usr_type

class Attribute:
    def __init__(self, name, path):
        self.name = name #name of struct
        self.path = path #path to member in struct

class Callable:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Operations:
    def __init__(self, operations):
        self.operations = operations

class Const:
    def __init__(self, const):
        self.const = const

class Name:
    def __init__(self, name):
        self.name = name

class Subscript:
    def __init__(self, name, index, path=None):
        self.name = name
        self.index = index
        #if we have path than this array in struct
        self.path = path #path to member in struct

class EmptyOperand:
    pass

class Operation:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


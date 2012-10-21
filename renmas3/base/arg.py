import platform
import inspect
from .vector3 import Vector3

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

class Vec3(Argument):

    def __init__(self, name, value):
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
                #TODO not tested yet
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

#TODO implement locking of map and list???
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
        elif hasattr(typ, 'struct'):
            typ_name, fields = typ.struct()
            usr_type = create_user_type(typ_name, fields)
            arg = Struct(name, usr_type)
        else:
            raise ValueError("Unknown type of arugment")
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

class Operands:
    def __init__(self, operands):
        self.operands = operands


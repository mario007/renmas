from ..core import Vector3

class Argument:
    def __init__(self, name):
        self.name = name

    def set_value(self, ds, value, path=None, idx_thread=None):
        raise NotImplementedError()

    def get_value(self, ds, value, path=None, idx_thread=None):
        raise NotImplementedError()

    def generate_data(self):
        raise NotImplementedError()


class ConstIntArg(Argument):
    def __init__(self, name, value=0):
        super(IntArg, self).__init__(name)
        #assert int
        self._value = value

    @property
    def value(self):
        return self._value

class ConstFloatArg(Argument):
    def __init__(self, name, value=0.0):
        super(IntArg, self).__init__(name)
        #assert float
        self._value = value

    @property
    def value(self):
        return self._value

class IntArg(Argument):

    def __init__(self, name, value=0):
        super(IntArg, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = int(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def set_value(self, ds, value, path=None, idx_thread=None):
        #TODO check type of value
        if path is not None:
            name = path 
        else:
            name = self.name

        if idx_thread is None:
            for d in ds:
                d[name] = value 
        else:
            ds[idx_thread][name] = value

    def get_value(self, ds, path=None, idx_thread=None):
        if path is not None:
            name = path 
        else:
            name = self.name
        if idx_thread is None:
            return ds[0][name]
        else:
            return ds[idx_thread][name]

    def generate_data(self):
        return 'int32 %s = %i \n' % (self.name, self._value) 

class FloatArg(Argument):

    def __init__(self, name, value=0.0):
        super(FloatArg, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = float(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def set_value(self, ds, value, path=None, idx_thread=None):
        #TODO check type of value
        if path is not None:
            name = path 
        else:
            name = self.name

        if idx_tread is None:
            for d in ds:
                d[name] = value 
        else:
            ds[idx_thread][name] = value

    def get_value(self, ds, path=None, idx_thread=None):
        if path is not None:
            name = path 
        else:
            name = self.name

        if idx_thread is None:
            return ds[0][name]
        else:
            return ds[idx_thread][name]

    def generate_data(self):
        return 'float %s = %f \n' % (self.name, self._value)

class Vector3Arg(Argument):

    def __init__(self, name, value):
        super(Vector3Arg, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def set_value(self, ds, value, path=None, idx_thread=None):
        #TODO check type of value
        #TODO think  is value can be tuple or list
        if path is not None:
            name = path 
        else:
            name = self.name
        if idx_thread is None:
            for d in ds:
                d[name] = value.to_ds() 
        else:
            ds[idx_thread][name] = value.to_ds()

    def get_value(self, ds, path=None, idx_thread=None):
        if path is not None:
            name = path 
        else:
            name = self.name
        if idx_thread is None:
            val = ds[0][name]
        else:
            val = ds[idx_thread][name]
        return Vector3(val[0], val[1], val[2])

    def generate_data(self):
        v = self._value
        return 'float %s[4] = %f,%f,%f,0.0 \n' % (self.name, v.x, v.y, v.z)

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
            if isinstance(arg, StructArg):
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

class StructArg(Argument):
    def __init__(self, name, typ):
        super(StructArg, self).__init__(name)
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

#TODO implement locking of map and list
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

def create_argument(name, value):
    if isinstance(value, int):
        arg = IntArg(name, value)
    elif isinstance(value, float):
        arg = FloatArg(name, value)
    elif isinstance(value, tuple) or isinstance(value, list):
        if len(value) != 3:
            raise ValueError('Wrong length of tuple', value)
        arg = Vector3Arg(name, Vector3(float(value[0]), float(value[1]), float(value[2])))
    elif isinstance(value, Vector3):
        arg = Vector3Arg(name, value)
    elif isinstance(value, UserType):
        arg = StructArg(name, value)
    else: #TODO tuple and list  for vector constants
        raise ValueError('Unknown value type', value)
    return arg

#a5 = create_user_type_(typ="point", fields=[('x', 55)])
def create_user_type(typ, fields):
    struct = UserType(typ)
    for n, v in fields:
        arg = create_argument(n, v)
        struct.add(arg)
    return struct


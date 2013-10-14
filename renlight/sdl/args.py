
from renlight.vector import Vector2, Vector3, Vector4


class Argument:
    """
    Abstract base class that define interface for type in shading language.
    All supported types in shading language must inherit this class.
    """
    def __init__(self, name):
        """Name of the argument."""
        self._name = name

    @property
    def name(self):
        return self._name


class IntArg(Argument):

    def __init__(self, name, value=0):
        super(IntArg, self).__init__(name)
        assert int is type(value)
        self._value = value

    def _set_value(self, value):
        assert int is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self, cgen):
        return 'int32 %s = %i \n' % (self.name, self._value)

    def update(self, ds, path=None):
        if path is None:
            ds[self.name] = self._value
        else:
            ds[path + self.name] = self._value

    def from_ds(self, ds, path=None):
        if path is None:
            val = ds[self.name]
        else:
            val = ds[path + self.name]
        self.value = val
        return val

    @classmethod
    def conv_to_ds(cls, obj):
        return int(obj)

    @classmethod
    def conv_to_obj(cls, val):
        return int(val)


class FloatArg(Argument):

    def __init__(self, name, value=0.0):
        super(FloatArg, self).__init__(name)
        assert float is type(value)
        self._value = value

    def _set_value(self, value):
        assert float is type(value)
        self._value = float(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self, cgen):
        return 'float %s = %f \n' % (self.name, self._value)

    def update(self, ds, path=None):
        if path is None:
            ds[self.name] = self._value
        else:
            ds[path + self.name] = self._value

    def from_ds(self, ds, path=None):
        if path is None:
            val = ds[self.name]
        else:
            val = ds[path + self.name]
        self.value = val
        return val

    @classmethod
    def conv_to_ds(cls, obj):
        return float(obj)

    @classmethod
    def conv_to_obj(cls, val):
        return float(val)


class Vec2Arg(Argument):

    def __init__(self, name, value=Vector2(0.0, 0.0)):
        super(Vec2Arg, self).__init__(name)
        assert Vector2 is type(value)
        self._value = value

    def _set_value(self, value):
        assert Vector2 is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self, cgen):
        v = self._value
        return 'float %s[4] = %f,%f,0.0,0.0 \n' % \
            (self.name, float(v.x), float(v.y))

    def update(self, ds, path=None):
        v = self._value
        if path is None:
            ds[self.name] = (float(v.x), float(v.y), 0.0, 0.0)
        else:
            ds[path + self.name] = (float(v.x), float(v.y), 0.0, 0.0)

    def from_ds(self, ds, path=None):
        if path is None:
            val = ds[self.name]
        else:
            val = ds[path + self.name]
        vec = self._value
        vec.x = val[0]
        vec.y = val[1]
        return vec


class Vec3Arg(Argument):

    def __init__(self, name, value=Vector3(0.0, 0.0, 0.0)):
        super(Vec3Arg, self).__init__(name)
        assert Vector3 is type(value)
        self._value = value

    def _set_value(self, value):
        assert Vector3 is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self, cgen):
        v = self._value
        return 'float %s[4] = %f,%f,%f,0.0 \n' % \
            (self.name, float(v.x), float(v.y), float(v.z))

    def update(self, ds, path=None):
        v = self._value
        if path is None:
            ds[self.name] = (float(v.x), float(v.y), float(v.z), 0.0)
        else:
            ds[path + self.name] = (float(v.x), float(v.y), float(v.z), 0.0)

    def from_ds(self, ds, path=None):
        if path is None:
            val = ds[self.name]
        else:
            val = ds[path + self.name]
        vec = self._value
        vec.x = val[0]
        vec.y = val[1]
        vec.z = val[2]
        return vec


class Vec4Arg(Argument):

    def __init__(self, name, value=Vector4(0.0, 0.0, 0.0, 0.0)):
        super(Vec4Arg, self).__init__(name)
        assert Vector4 is type(value)
        self._value = value

    def _set_value(self, value):
        assert Vector4 is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self, cgen):
        v = self._value
        return 'float %s[4] = %f,%f,%f,%f \n' % \
            (self.name, float(v.x), float(v.y), float(v.z), float(v.w))

    def update(self, ds, path=None):
        v = self._value
        vals = (float(v.x), float(v.y), float(v.z), float(v.w))
        if path is None:
            ds[self.name] = vals
        else:
            ds[path + self.name] = vals

    def from_ds(self, ds, path=None):
        if path is None:
            val = ds[self.name]
        else:
            val = ds[path + self.name]
        vec = self._value
        vec.x = val[0]
        vec.y = val[1]
        vec.z = val[2]
        vec.w = val[3]
        return vec


class StructDesc:
    def __init__(self, typ, type_name, fields, factory):
        self.typ = typ
        self.type_name = type_name
        self.fields = fields
        self.factory = factory

_struct_desc = {}


def register_struct(typ, type_name, fields, factory=None):
    desc = StructDesc(typ, type_name, fields, factory)
    _struct_desc[typ] = desc
    _struct_desc[type_name] = desc


class StructArg(Argument):
    def __init__(self, name, value):
        super(StructArg, self).__init__(name)
        if type(value) not in _struct_desc:
            raise ValueError("This structure is not registerd!", type(value))
        self._value = value

        self._args = []
        desc = _struct_desc[type(value)]
        for arg_name, arg_type in desc.fields:
            val = getattr(value, arg_name)
            arg = arg_type(arg_name, val)
            self._args.append(arg)

    @property
    def args(self):
        return self._args

    @property
    def type_name(self):
        return _struct_desc[type(self._value)].type_name

    def _set_value(self, value):
        assert type(self._value) is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self, cgen):
        return '%s %s\n' % (self.type_name, self.name)

    def update(self, ds, prefix=''):
        for arg in self._args:
            if isinstance(arg, StructArg):
                prefix = prefix + self.name + '.'
                arg.update(ds, prefix=prefix)
            else:
                if prefix == '':
                    path = '%s.' % self.name
                else:
                    path = '%s%s.' % (prefix, self.name)
                arg.update(ds, path=path)

    def from_ds(self, ds, prefix=''):
        for arg in self._args:
            #TODO Test FIX struct inside struct
            if isinstance(arg, StructArg):
                prefix = prefix + self.name + '.'
                arg.from_ds(ds, prefix=prefix)
            else:
                if prefix == '':
                    path = '%s.' % self.name
                else:
                    path = '%s%s.' % (prefix, self.name)
                val = arg.from_ds(ds, path=path)
                setattr(self._value, arg.name, val)
        return self._value

    def resolve(self, path):
        comps = path.split('.')
        for arg in self._args:
            if arg.name == comps[0]:
                if len(comps) == 1:
                    return arg
                else:
                    if not isinstance(arg, StructArg):
                        raise ValueError('Struct argument is expected', arg)
                    return arg.resolve('.'.join(comps[1:]))
        raise ValueError("Could not resove path ", path)

    def struct_def(self, cgen):
        code = "struct %s \n" % _struct_desc[type(self._value)].type_name
        for a in self._args:
            code += a.generate_data(cgen)
        code += "end struct \n\n"
        return code


class StructArgPtr(StructArg):
    def generate_data(self, cgen):
        if cgen.BIT64:
            return 'uint64 %s\n' % self.name
        else:
            return 'uint32 %s\n' % self.name


class ArgList(Argument):
    """
        All arguments must have same type and name.
    """
    def __init__(self, name, args):
        typ = type(args[0])
        if not all(typ is type(arg) for arg in args):
            raise ValueError("All arguments must have same type")
        if not all(name == arg.name for arg in args):
            raise ValueError("All arguments must have same name")

        self._args = args

    def _set_value(self, lst_values):
        for value, arg in zip(lst_values, self._args):
            arg.value = value

    def _get_value(self):
        values = [arg.value for arg in self._args]
        return values
    value = property(_get_value, _set_value)

    def update(self, ds):
        for d, arg in zip(ds, self._args):
            arg.update(d)

    def generate_data(self, cgen):
        return self._args[0].generate_data(cgen)

    def from_ds(self, ds):
        vals = [arg.from_ds(d) for d, arg in zip(ds, self._args)]
        return vals


def arg_from_value(name, value):
    if type(value) in _struct_desc:
        arg = StructArg(name, value)
    elif isinstance(value, int):
        arg = IntArg(name, value)
    elif isinstance(value, float):
        arg = FloatArg(name, value)
    elif isinstance(value, (list, tuple)):
        if len(value) == 2:
            arg = Vec2Arg(name, Vector2.create(*value))
        elif len(value) == 3:
            arg = Vec3Arg(name, Vector3.create(*value))
        elif len(value) == 4:
            arg = Vec4Arg(name, Vector4.create(*value))
        else:
            raise ValueError("List or tuple is two big!", value)
    else:
        raise ValueError("Unknown type of value", type(value), value)
    return arg

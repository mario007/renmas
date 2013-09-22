
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

    def update(self, ds):
        ds[self.name] = self._value

    def from_ds(self, ds):
        val = ds[self.name]
        self.value = val
        return val


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

    def update(self, ds):
        ds[self.name] = self._value

    def from_ds(self, ds):
        val = ds[self.name]
        self.value = val
        return val


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

    def update(self, ds):
        v = self._value
        ds[self.name] = (float(v.x), float(v.y), 0.0, 0.0)

    def from_ds(self, ds):
        val = ds[self.name]
        vec = Vector2(val[0], val[1])
        self.value = vec
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

    def update(self, ds):
        v = self._value
        ds[self.name] = (float(v.x), float(v.y), float(v.z), 0.0)

    def from_ds(self, ds):
        val = ds[self.name]
        vec = Vector3(val[0], val[1], val[2])
        self.value = vec
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

    def update(self, ds):
        v = self._value
        ds[self.name] = (float(v.x), float(v.y), float(v.z), float(v.w))

    def from_ds(self, ds):
        val = ds[self.name]
        vec = Vector4(val[0], val[1], val[2], val[3])
        self.value = vec
        return vec


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
    if isinstance(value, int):
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


class Argument:
    def __init__(self, name):
        self.name = name

    def set_value(self, ds, value, idx_thread=None):
        raise NotImplementedError()

    def get_value(self, ds, value, idx_thread=None):
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

    def set_value(self, ds, value, idx_thread=None):
        #TODO check type of value
        if idx_thread is None:
            for d in ds:
                d[self.name] = value 
        else:
            ds[idx_thread][self.name] = value

    def get_value(self, ds, idx_thread=None):
        if idx_thread is None:
            return ds[0][self.name]
        else:
            return ds[idx_thread][self.name]

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

    def set_value(self, ds, value, idx_thread=None):
        #TODO check type of value
        if idx_tread is None:
            for d in ds:
                d[self.name] = value 
        else:
            ds[idx_thread][self.name] = value

    def get_value(self, ds, idx_thread=None):
        if idx_thread is None:
            return ds[0][self.name]
        else:
            return ds[idx_thread][self.name]

    def generate_data(self):
        return 'float %s = %f \n' % (self.name, self._value)

class Vector3Arg(Argument):

    def __init__(self, name, value):
        super(IntArg, self).__init__(name)
        self._value = value

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)


def create_argument(name, value):
    if isinstance(value, int):
        arg = IntArg(name, value)
    elif isinstance(value, float):
        arg = FloatArg(name, value)
    else: #TODO tuple and list  for vector constants
        raise ValueError('Unknown value type', value)
    return arg


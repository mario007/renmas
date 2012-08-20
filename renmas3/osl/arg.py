
class Argument:
    def __init__(self):
        pass

    def to_reg(self, reg):
        pass

class ConstIntArg(Argument):
    def __init__(self, name, value):
        self.name = name
        self._value = value

    @property
    def value(self):
        return self._value

class ConstFloatArg(Argument):
    def __init__(self, name, value):
        self.name = name
        self._value = value

    @property
    def value(self):
        return self._value

class IntArg(Argument):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def _set_value(self, value):
        self._value = int(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)


class FloatArg(Argument):

    def __init__(self, name, value):
        self.name = name

    def _set_value(self, value):
        self._value = float(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

class Vector3Arg(Argument):

    def __init__(self, name, value):
        self.name = name

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)



from tdasm import Tdasm
from .dynamic_array import DynamicArray
from .args import arg_from_value, StructArg, _struct_desc, Argument


class Array:
    def __init__(self, value):
        arg = arg_from_value('p1', value)
        if not isinstance(arg, StructArg):
            raise ValueError("Only struct arugment for now in array!", arg)

        from .cgen import CodeGenerator
        struct_def = arg.struct_def(CodeGenerator())
        struct = self._create_struct(struct_def, arg.type_name)
        self._dyn_arr = DynamicArray(struct)
        self._arg = arg

    def append(self, obj):
        typ = type(obj)
        if not isinstance(self._arg.value, typ):
            raise ValueError("Uncompatable types for array", obj)
        desc = _struct_desc[type(self._arg.value)]
        values = {}
        #TODO struct inside struct
        for name, arg_type in desc.fields:
            val = getattr(obj, name)
            values[name] = arg_type.conv_to_ds(val)
        self._dyn_arr.add_instance(values)

    def _create_struct(self, struct_def, name):
        code = " #DATA \n" + struct_def + """
        #CODE
        #END
        """
        mc = Tdasm().assemble(code)
        return mc.get_struct(name)

    def __getitem__(self, key):
        if key >= self._dyn_arr.size:
            raise IndexError("Key is out of bounds! ", key)

        values = self._dyn_arr.get_instance(key)
        desc = _struct_desc[type(self._arg.value)]
        obj = desc.factory()
        for name, arg_type in desc.fields:
            value = arg_type.conv_to_obj(values[name])
            setattr(obj, name, value)
        return obj

    def __len__(self):
        return self._dyn_arr.size

    def address(self):
        return self._dyn_arr.address_info()

    @property
    def type_name(self):
        return self._arg.type_name

    @property
    def item_size(self):
        return self._dyn_arr.obj_size()

    @property
    def item_arg(self):
        return self._arg


class ArrayArg(Argument):
    def __init__(self, name, value):
        super(ArrayArg, self).__init__(name)
        assert Array is type(value)
        self._value = value

    def _set_value(self, value):
        assert Array is type(value)
        assert self._value.type_name == value.type_name
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def update(self, ds, path=None):
        ptr = self._value.address()
        if path is None:
            ds[self.name] = ptr
        else:
            ds[path + self.name] = ptr

    def generate_data(self, cgen):
        if cgen.BIT64:
            return 'uint64 %s\n' % self.name
        else:
            return 'uint32 %s\n' % self.name

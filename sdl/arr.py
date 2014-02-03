
import platform
from tdasm import Tdasm
import x86
from .dynamic_array import DynamicArray
from .args import arg_from_value, StructArg, _struct_desc, Argument
from .memcpy import memcpy


class Array:
    def __init__(self):
        pass


class ObjArray(Array):
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
        ia32 = True
        bits = platform.architecture()[0]
        if bits == '64bit':
            ia32 = False
        mc = Tdasm().assemble(code, ia32=ia32)
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


class PtrsArray(Array):
    def __init__(self, reserve=0):
        self._reserve = reserve
        if reserve == 0:
            self._reserve = 1
        self._size = 0
        self._item_size = 4
        self.BIT64 = False
        bits = platform.architecture()[0]
        if bits == '64bit':
            self._item_size = 8
            self.BIT64 = True

        self._address = x86.MemData(self._reserve*self._item_size)

    def append(self, value):
        if not isinstance(value, int):
            raise ValueError("Integer value is expected!", value)
        if self._reserve == self._size:
            self._resize()

        offset = self._item_size * self._size
        if self.BIT64:
            x86.SetUInt64(self._address.ptr() + offset, value, 0)
        else:
            x86.SetUInt32(self._address.ptr() + offset, value, 0)
        self._size += 1

    def __getitem__(self, key):
        if key >= self._size:
            raise IndexError("Key is out of bounds! ", key)

        offset = self._item_size * self._size
        if self.BIT64:
            return x86.GetUInt64(self._address.ptr() + offset, 0, 0)
        else:
            return x86.GetUInt32(self._address.ptr() + offset, 0, 0)

    def __len__(self):
        return self._size

    def address(self):
        return self._address.ptr()  

    @property
    def item_size(self):
        return self._item_size

    @property
    def type_name(self):
        return 'ptrs'

    def _resize(self):
        if self._size >= 0 and self._size <= 100:
            self._reserve += 1
        elif self._size > 100 and self._size <= 10000:
            self._reserve += 100
        elif self._size > 10000 and self._size <= 1000000:
            self._reserve += 10000
        else:
            self._reserve += 100000

        temp = x86.MemData(self._item_size*self._reserve)
        memcpy(temp.ptr(), self._address.ptr(), self._size*self._item_size) 
        self._address = temp


class ArrayArg(Argument):
    def __init__(self, name, value):
        super(ArrayArg, self).__init__(name)
        assert isinstance(value, Array)
        self._value = value

    def _set_value(self, value):
        assert isinstance(value, Array)
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

    def from_ds(self, ds, path=None):
        return self._value

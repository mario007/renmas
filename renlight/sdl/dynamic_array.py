
import x86
from struct import unpack, pack
import array
from renlight.memcpy import memcpy


class DynamicArray:
    def __init__(self, struct, reserve=0):
        self.size = 0
        self.struct = struct
        self.sizeof = struct.sizeof()
        self.members = {}
        self.members2 = {}
        self.reserve = reserve
        self.bytes = array.array("B", B'\x00' * struct.sizeof())

        for key, value in struct.members.items():
            name = key
            data_type, value, is_array, arr_length, offset = value
            self._register_member(name, value, data_type, offset, is_array, arr_length)

        self.bytes = bytes(self.bytes)

        if self.reserve > 0:
            self.address = x86.MemData(self.reserve*self.sizeof)
        else:
            self.address = None

    def address_info(self):
        if self.address is not None:
            return self.address.ptr()
        return None

    def obj_size(self):  # size in bytes
        return self.sizeof

    def num_objects(self):  # number of objects in array
        return self.size

    def get_name_struct(self):
        return self.struct.name

    def member_offset(self, name):
        offset, fn, array, length = self.members2[name]
        return offset

    def add_instance(self, instance):
        if self.address is None:
            self.address = x86.MemData(self.sizeof)
            self.reserve += 1
        elif self.reserve == self.size:
            if self.size > 0 and self.size <= 100:
                self.reserve += 1
            elif self.size > 100 and self.size <= 10000:
                self.reserve += 100
            elif self.size > 10000 and self.size <= 1000000:
                self.reserve += 10000
            else:
                self.reserve += 100000

            temp = x86.MemData(self.sizeof*self.reserve)
            memcpy(temp.ptr(), self.address.ptr(), self.size*self.sizeof)
            self.address = temp

        offset = self.sizeof * self.size
        x86.SetData(self.address.ptr() + offset, self.bytes)
        for key, value in instance.items():
            self._set_member(key, value, self.size)
        self.size += 1

    def add_default_instances(self, n): #TODO improve performnase of this!

        for k in range(n):
            if self.address is None:
                self.address = x86.MemData(self.sizeof)
                self.reserve += 1
            elif self.reserve == self.size:
                if self.size > 0 and self.size <= 100:
                    self.reserve += 1
                elif self.size > 100 and self.size <= 10000:
                    self.reserve += 100
                elif self.size > 10000 and self.size <= 1000000:
                    self.reserve += 10000
                else:
                    self.reserve += 100000

                temp = x86.MemData(self.sizeof*self.reserve)
                memcpy(temp.ptr(), self.address.ptr(), self.size*self.sizeof)
                self.address = temp

            offset = self.sizeof * self.size
            x86.SetData(self.address.ptr() + offset, self.bytes)
            self.size += 1

    def edit_instance(self, index, instance):
        if index < 0 or index >= self.size:
            return None  # out of bounds
        for key, value in instance.items():
            self._set_member(key, value, index)

    def get_instance(self, index):
        if index < 0 or index >= self.size:
            return None  # out of bounds
        d = {}
        for key in self.members.keys():
            d[key] = self._get_member(key, index)
        return d

    def _register_member(self, name, value, typ, offset, array=False, arr_length=0):
        if typ == 'string' and array: return False # array of strings are not supported
        if type == 'string' and value is None: return False # string must have value

        flags = {'uint8': 'B', 'int8': 'b', 'uint16': 'H', 'int16':'h',
                'uint32': 'I', 'int32':'i', 'float': 'f', 'double': 'd',
                'int64': 'q', 'uint64': 'Q' }
        if typ == "string":
            flags['string'] = str(len(value)) + 's'

        if value is not None:
            if isinstance(value, tuple) or isinstance(value, list):
                num_bytes = b''
                for x in value:
                    num_bytes += pack(flags[typ], x)
            else:
                num_bytes = pack(flags[typ], value)

        if value is not None:
            addr = self.bytes.buffer_info()[0] 
            x86.SetData(addr + offset, num_bytes)

        var_types = {"int8":x86.GetInt8, "int16":x86.GetInt16, 
                    "int32":x86.GetInt32, "uint8":x86.GetUInt8,
                    "uint16":x86.GetUInt16, "uint32":x86.GetUInt32,
                    "int64" :x86.GetInt64, "uint64": x86.GetUInt64,
                    "float":x86.GetFloat, "double":x86.GetDouble }
        var_types2 = {"int8":x86.SetInt8, "int16":x86.SetInt16,
                "int32":x86.SetInt32, "uint8":x86.SetUInt8,
                "uint16":x86.SetUInt16, "uint32":x86.SetUInt32,
                "int64": x86.SetInt64, "uint64": x86.SetUInt64,
                "float":x86.SetFloat, "double":x86.SetDouble }

        def get_string(address, size, flags):
            def get_mem(addr, dummy2, dummy3):
                num_bytes = x86.GetData(addr, size)
                ret = unpack(flags, num_bytes[:])
                if len(ret) == 1:
                    return ret[0]
                return ret
            return get_mem

        if typ == "string":
            fn = get_string(offset, len(value), flags[typ])
            self.members[name] = (offset, fn, array, arr_length)
        else:
            self.members[name] = (offset, var_types[typ], array, arr_length)
            self.members2[name] = (offset, var_types2[typ], array, arr_length)

    def _get_member(self, name, index):
        offset, fn, array, length = self.members[name]
        addr = self.address.ptr() + index * self.sizeof + offset
        if array:
            return fn(addr, 0, length)  # return whole array
        else:
            return fn(addr, 0, 0)

    def _set_member(self, name, value, index):
        if value is None:
            return False  # TODO maybe exception???
        offset, fn, array, length = self.members2[name]
        addr = self.address.ptr() + index * self.sizeof + offset
        if array:  # value must be tuple, c++ doesn't check for list
            return fn(addr, value, 0)
        else:
            return fn(addr, value, 0)



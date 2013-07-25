
import x86
from struct import unpack, pack
from .memcopy import memcpy

class Array:
    def __init__(self, item_size, reserve=0):
        self._size = 0
        self._reserve = reserve 
        self._item_size = item_size
        if reserve < 1:
            self._reserve = 1

        self._address = x86.MemData(self._reserve * self._item_size)

    def extend(self, iterable):
        for val in iterable:
            self.append(val)

    def append(self, value):
        if self._reserve == self._size:
            if self._size > 0 and self._size <= 100:
                self._reserve += 1
            elif self._size > 100 and self._size <= 10000:
                self._reserve += 100
            elif self._size > 10000 and self._size <= 1000000:
                self._reserve += 10000
            else:
                self._reserve += 100000

            temp = x86.MemData(self._item_size * self._reserve)
            memcpy(temp.ptr(), self._address.ptr(), self._size * self._item_size)
            self._address = temp

        offset = self._item_size * self._size
        addr = self._address.ptr() + offset
        self._append(addr, value)
        self._size += 1

    def _append(self, addr, value):
        """This must be implemented in derivied class."""
        raise NotImplementedError()

    def _get_item(self, addr):
        """This must be implemented in derivied class."""
        raise NotImplementedError()

    def __getitem__(self, key):
        if key >= self._size:
            raise IndexError("Key is out of bounds! ", key)
        offset = self._item_size * key
        addr = self._address.ptr() + offset
        return self._get_item(addr)

    def __len__(self):
        return self._size

class FloatArray(Array):
    def __init__(self, reserve=0, values=()):
        super(FloatArray, self).__init__(4, reserve=reserve)
        self.extend(values)

    def _append(self, addr, value):
        x86.SetFloat(addr, float(value), 0)

    def _get_item(self, addr):
        return x86.GetFloat(addr, 0, 0)

    def pop(self, index):
        pass

    def remove(self, val):
        pass

class Int32Array(Array):
    pass

class Int64Array(Array):
    pass


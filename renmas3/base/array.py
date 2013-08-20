
import x86
from struct import unpack, pack
from .memcopy import memcpy

from .integer import Integer
from .pointer import Pointer

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
        self._set_item(addr, value)
        self._size += 1

    def _set_item(self, addr, value):
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
    
    def __setitem__(self, key, value):
        if key >= self._size:
            raise IndexError("Key is out of bounds! ", key)
        offset = self._item_size * key
        addr = self._address.ptr() + offset
        self._set_item(addr, value)

    def __len__(self):
        return self._size

    ## Return address of array 
    # @param self The object pointer
    # @return Return address of array
    @property
    def address(self):
        return self._address.ptr()

class FloatArray(Array):
    def __init__(self, reserve=0, values=()):
        super(FloatArray, self).__init__(4, reserve=reserve)
        self.extend(values)

    def _set_item(self, addr, value):
        x86.SetFloat(addr, float(value), 0)

    def _get_item(self, addr):
        return x86.GetFloat(addr, 0, 0)

    def pop(self, index):
        pass

    def remove(self, val):
        pass

    @classmethod
    def user_type(cls):
        typ_name = "FloatArray"
        fields = [('address', Pointer)]
        return (typ_name, fields)

class Int32Array(Array):
    pass

class Int64Array(Array):
    pass

class Array2D:
    def __init__(self, width, height, item_size):
        self._width = width
        self._height = height
        self._item_size = item_size
        self._address = x86.MemData(width * height * item_size)

    def __getitem__(self, key):
        x, y = key
        if x >= self._width or y >= self._height:
            raise IndexError("Key is out of bounds! ", key)
        offset = self._width * self._item_size * y + x * self._item_size
        addr = self._address.ptr() + offset
        return self._get_item(addr)
    
    def __setitem__(self, key, value):
        x, y = key
        if x >= self._width or y >= self._height:
            raise IndexError("Key is out of bounds! ", key)
        offset = self._width * self._item_size * y + x * self._item_size
        addr = self._address.ptr() + offset
        self._set_item(addr, value)

    ## Return address of array 
    # @param self The object pointer
    # @return Return address of array
    @property
    def address(self):
        return self._address.ptr()

    ## Return width of array 
    # @param self The object pointer
    # @return Return width of array
    @property
    def width(self):
        return self._width

    ## Return height of array 
    # @param self The object pointer
    # @return Return height of array
    @property
    def height(self):
        return self._height

    ## Return pitch of array 
    # @param self The object pointer
    # @return Return pitch of array
    @property
    def pitch(self):
        return self._width * self._item_size

class FloatArray2D(Array2D):
    def __init__(self, width, height):
        super(FloatArray2D, self).__init__(width=width, height=height, item_size=4)

    def _get_item(self, addr):
        return x86.GetFloat(addr, 0, 0)

    def _set_item(self, addr, value):
        x86.SetFloat(addr, float(value), 0)

    @classmethod
    def user_type(cls):
        typ_name = "FloatArray2D"
        fields = [('address', Pointer), ('width', Integer), ('height', Integer), ('pitch', Integer)]
        return (typ_name, fields)


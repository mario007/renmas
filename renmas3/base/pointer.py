
import platform
from .arg import Argument, check_ptr_reg

class Pointer(Argument):
    def __init__(self, name, typ=None, value=0):
        super(Pointer, self).__init__(name)
        self._typ = typ
        self._value = value

    @property
    def typ(self):
        return self._typ

    def _set_value(self, value):
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            return 'uint64 %s = %i \n' % (self.name, self._value) 
        else:
            return 'uint32 %s = %i \n' % (self.name, self._value) 

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        if idx_thread is None:
            for d in ds:
                d[path] = value 
        else:
            ds[idx_thread][path] = value

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            return ds[0][path]
        else:
            return ds[idx_thread][path]

    @classmethod
    def load_attr(cls, cgen, path, ptr_reg, dest_reg=None):
        if dest_reg is None:
            if cgen.BIT64:
                dest_reg = cgen.register(typ='general', bit=64)
            else:
                dest_reg = cgen.register(typ='general', bit=32)
        check_ptr_reg(cgen, ptr_reg)
        check_ptr_reg(cgen, dest_reg)
        if cgen.BIT64:
            code = "mov %s, qword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "mov %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, Pointer


from .vector3 import Vector2, Vector3, Vector4
from .vector3 import Vector2I, Vector3I, Vector4I
from .arg import Argument, conv_int_to_float, check_ptr_reg
from .integer import Integer, Float
from .util import float2hex

class _Vec234(Argument):

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)

        if cgen.AVX:
            code = "vmovaps %s, oword [%s] \n" % (dest_reg, self.name)
        else:
            code = "movaps %s, oword [%s] \n" % (dest_reg, self.name)
        return code, dest_reg, type(self)

    def store_cmd(self, cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)
        if cgen.AVX:
            code = "vmovaps oword [%s], %s \n" % (self.name, xmm)
        else:
            code = "movaps oword [%s], %s \n" % (self.name, xmm)
        return code

    @classmethod
    def load_attr(cls, cgen, path, ptr_reg, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)
        check_ptr_reg(cgen, ptr_reg)
        if cgen.AVX:
            code = "vmovaps %s, oword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "movaps %s, oword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, cls

    @classmethod
    def load_subscript_attr(cls, cgen, path, index, ptr_reg, dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)
        if not cls.index_in_range(index):
            raise ValueError("Index is out of allowed range!", cls, index)
        check_ptr_reg(cgen, ptr_reg)
        offset = index * 4
        if cgen.AVX:
            code = "vmovss %s, dword [%s + %s + %i]\n" % (dest_reg, ptr_reg, path, offset)
        else:
            code = "movss %s, dword [%s + %s + %i]\n" % (dest_reg, ptr_reg, path, offset)
        return code, dest_reg, Float

    @classmethod
    def store_attr(cls, cgen, path, ptr_reg, xmm):
        if not cgen.regs.is_xmm(xmm):
             raise ValueError("xmm register is expected!", xmm)
        check_ptr_reg(cgen, ptr_reg)
        if cgen.AVX:
            code = "vmovaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code = "movaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code

    @classmethod
    def store_subscript_attr(cls, cgen, path, ptr_reg, reg, typ, index):
        xmm = reg
        code = ''
        if typ == Integer:
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg, xmm)
        check_ptr_reg(cgen, ptr_reg)

        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)
        if not cls.index_in_range(index):
            raise ValueError("Index is out of allowed range!", cls, index)
        offset = index * 4
        if cgen.AVX:
            code += "vmovss dword [%s + %s + %i], %s \n" % (ptr_reg, path, offset, xmm)
        else:
            code += "movss dword [%s + %s + %i], %s \n" % (ptr_reg, path, offset, xmm)
        if xmm != reg:
            cgen.release_reg(xmm)
        return code

    @classmethod
    def index_in_range(cls, index):
        raise NotImplementedError()

    def load_subscript(self, cgen, index, dest_reg=None):
        #NOTE Only consts for index TODO for name, attribute etc.
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)
        if not self.index_in_range(index):
            raise ValueError("Index is out of allowed range!", self, index)
        offset = index * 4
        if cgen.AVX:
            code = "vmovss %s, dword [%s + %i] \n" % (dest_reg, self.name, offset)
        else:
            code = "movss %s, dword [%s + %i] \n" % (dest_reg, self.name, offset)
        return code, dest_reg, Float

    def store_subscript(self, cgen, reg, typ, index):
        xmm = reg
        code = ''
        if typ == Integer:
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg, xmm)

        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)
        if not self.index_in_range(index):
            raise ValueError("Index is out of allowed range!", self, index)
        offset = 4 * index
        if cgen.AVX:
            code += "vmovss dword [%s + %i], %s \n" % (self.name, offset, xmm)
        else:
            code += "movss dword [%s + %i], %s \n" % (self.name, offset, xmm)
        if xmm != reg:
            cgen.release_reg(xmm)
        return code

    @classmethod
    def neg_cmd(cls, cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)

        arg = cgen.create_const((-1.0, -1.0, -1.0, -1.0))
        if cgen.AVX:
            code = "vmulps %s, %s, oword[%s]\n" % (xmm, xmm, arg.name) 
        else:
            code = "mulps %s, oword[%s]\n" % (xmm, arg.name) 
        return code

    @classmethod
    def supported(cls, operator, typ):
        if operator == '*':
            if typ == Integer or typ == Float or typ == cls:
                return True
        if operator not in ('+', '-', '/', '*'):
            return False
        if typ != cls:
            return False
        return True

    @classmethod
    def _conv(cls, cgen, reg2, typ2, operator):
        code = ''
        xmm = reg2
        if typ2 == Integer and operator == '*':
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg2, xmm)
            typ2 = Float

        if typ2 == Float and operator == '*':
            if cgen.AVX: #vblends maybe is faster investigate TODO
                code += "vshufps %s, %s, %s, 0x00\n" % (xmm, xmm, xmm)
            else:
                code += "shufps %s, %s, 0x00\n" % (xmm, xmm)
        return code, xmm

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if not cgen.regs.is_xmm(reg1):
            raise ValueError('Destination register must be xmm register', reg1)

        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)

        code, xmm = cls._conv(cgen, reg2, typ2, operator)

        ops_avx = {'+': 'vaddps', '-': 'vsubps', '*': 'vmulps', '/': 'vdivps'}
        ops = {'+': 'addps', '-': 'subps', '*': 'mulps', '/': 'divps'}
        if cgen.AVX:
            code += "%s %s, %s, %s \n" % (ops_avx[operator], reg1, reg1, xmm)
        else:
            code += "%s %s, %s \n" % (ops[operator], reg1, xmm)
        return code, reg1, cls

    @classmethod
    def rev_arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if not cgen.regs.is_xmm(reg1):
            raise ValueError('Destination register must be xmm register', reg1)

        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)

        code, xmm = cls._conv(cgen, reg2, typ2, operator)
        code3, reg3, typ3 = cls.arith_cmd(cgen, xmm, reg1, cls, operator)

        return code + code3, reg3, typ3

    @classmethod
    def item_supported(cls, typ):
        if typ == Integer or typ == Float:
            return True
        return False

    @classmethod
    def register_type(cls):
        return 'xmm'

class Vec2(_Vec234):
    def __init__(self, name, value=Vector2(0.0, 0.0)):
        super(Vec2, self).__init__(name)
        assert Vector2 is type(value)
        self._value = value

    def _set_value(self, value):
        assert Vector2 is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert Vector2 is type(value)
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds() 
        else:
            ds[idx_thread][path] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector2(val[0], val[1])

    def generate_data(self):
        v = self._value
        return 'float %s[4] = %f,%f,0.0,0.0 \n' % (self.name, v.x, v.y)

    def store_const(self, cgen, const):
        if not isinstance(const, (tuple, list)) and len(const) != 2:
            raise ValueError("Tuple constat of 2 element is expected", const)
        fl = float2hex(float(const[0]))
        line1 = 'mov dword [%s], %s ;float value = %f \n' % (self.name, fl, const[0])
        fl = float2hex(float(const[1]))
        line2 = 'mov dword [%s + 4], %s ;float value = %f \n' % (self.name, fl, const[1])
        return line1 + line2

    @classmethod
    def store_attr_const(cls, cgen, path, ptr_reg, const):
        if not isinstance(const, (tuple, list)) and len(const) != 2:
            raise ValueError("Tuple constat of 2 element is expected", const)
        check_ptr_reg(cgen, ptr_reg)

        fl = float2hex(float(const[0]))
        line1 = "mov dword [%s + %s], %s ;float value = %f \n" % (ptr_reg, path, fl, const[0])
        fl = float2hex(float(const[1]))
        line2 = "mov dword [%s + %s + 4], %s ;float value = %f \n" % (ptr_reg, path, fl, const[1])
        return line1 + line2

    @classmethod
    def index_in_range(cls, index):
        if index != 0 and index != 1:
            return False
        return True

class Vec3(_Vec234):
    def __init__(self, name, value=Vector3(0.0, 0.0, 0.0)):
        super(Vec3, self).__init__(name)
        assert Vector3 is type(value)
        self._value = value

    def _set_value(self, value):
        assert Vector3 is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert Vector3 is type(value)
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds() 
        else:
            ds[idx_thread][path] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector3(val[0], val[1], val[2])

    def generate_data(self):
        v = self._value
        return 'float %s[4] = %f,%f,%f,0.0 \n' % (self.name, v.x, v.y, v.z)

    def store_const(self, cgen, const):
        if not isinstance(const, (tuple, list)) and len(const) != 3:
            raise ValueError("Tuple constat of 3 element is expected", const)
        fl = float2hex(float(const[0]))
        line1 = 'mov dword [%s], %s ;float value = %f \n' % (self.name, fl, const[0])
        fl = float2hex(float(const[1]))
        line2 = 'mov dword [%s + 4], %s ;float value = %f \n' % (self.name, fl, const[1])
        fl = float2hex(float(const[2]))
        line3 = 'mov dword [%s + 8], %s ;float value = %f \n' % (self.name, fl, const[2])
        return line1 + line2 + line3

    @classmethod
    def store_attr_const(cls, cgen, path, ptr_reg, const):
        if not isinstance(const, (tuple, list)) and len(const) != 3:
            raise ValueError("Tuple constat of 3 element is expected", const)
        check_ptr_reg(cgen, ptr_reg)

        fl = float2hex(float(const[0]))
        line1 = "mov dword [%s + %s], %s ;float value = %f \n" % (ptr_reg, path, fl, const[0])
        fl = float2hex(float(const[1]))
        line2 = "mov dword [%s + %s + 4], %s ;float value = %f \n" % (ptr_reg, path, fl, const[1])
        fl = float2hex(float(const[2]))
        line3 = "mov dword [%s + %s + 8], %s ;float value = %f \n" % (ptr_reg, path, fl, const[2])
        return line1 + line2 + line3

    @classmethod
    def index_in_range(cls, index):
        if index >= 0 and index <= 2:
            return True
        return True

class Vec4(_Vec234):
    def __init__(self, name, value=Vector4(0.0, 0.0, 0.0, 0.0)):
        super(Vec4, self).__init__(name)
        assert Vector4 is type(value)
        self._value = value

    def _set_value(self, value):
        assert Vector4 is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert Vector4 is type(value)
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds() 
        else:
            ds[idx_thread][path] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector4(val[0], val[1], val[2], val[3])

    def generate_data(self):
        v = self._value
        return 'float %s[4] = %f,%f,%f,%f \n' % (self.name, v.x, v.y, v.z, v.w)

    def store_const(self, cgen, const):
        if not isinstance(const, (tuple, list)) and len(const) != 4:
            raise ValueError("Tuple constat of 2 element is expected", const)
        fl = float2hex(float(const[0]))
        line1 = 'mov dword [%s], %s ;float value = %f \n' % (self.name, fl, const[0])
        fl = float2hex(float(const[1]))
        line2 = 'mov dword [%s + 4], %s ;float value = %f \n' % (self.name, fl, const[1])
        fl = float2hex(float(const[2]))
        line3 = 'mov dword [%s + 8], %s ;float value = %f \n' % (self.name, fl, const[2])
        fl = float2hex(float(const[3]))
        line4 = 'mov dword [%s + 12], %s ;float value = %f \n' % (self.name, fl, const[3])
        return line1 + line2 + line3 + line4

    @classmethod
    def store_attr_const(cls, cgen, path, ptr_reg, const):
        if not isinstance(const, (tuple, list)) and len(const) != 4:
            raise ValueError("Tuple constat of 2 element is expected", const)
        check_ptr_reg(cgen, ptr_reg)

        fl = float2hex(float(const[0]))
        line1 = "mov dword [%s + %s], %s ;float value = %f \n" % (ptr_reg, path, fl, const[0])
        fl = float2hex(float(const[1]))
        line2 = "mov dword [%s + %s + 4], %s ;float value = %f \n" % (ptr_reg, path, fl, const[1])
        fl = float2hex(float(const[2]))
        line3 = "mov dword [%s + %s + 8], %s ;float value = %f \n" % (ptr_reg, path, fl, const[2])
        fl = float2hex(float(const[3]))
        line4 = "mov dword [%s + %s + 12], %s ;float value = %f \n" % (ptr_reg, path, fl, const[3])
        return line1 + line2 + line3 + line4

    @classmethod
    def index_in_range(cls, index):
        if index >= 0 and index <= 3:
            return True
        return True

class _Vec234I(Argument):
    pass

    @classmethod
    def register_type(cls):
        return 'xmm'

class Vec2I(_Vec234I):
    def __init__(self, name, value=Vector2I(0, 0)):
        super(Vec2I, self).__init__(name)
        assert Vector2I is type(value)
        self._value = value

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert Vector2I is type(value)
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds()
        else:
            ds[idx_thread][path] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector2I(val[0], val[1])

    def _set_value(self, value):
        assert Vector2I is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        v = self._value
        return 'int32 %s[4] = %i,%i,0,0\n' % (self.name, int(v.x), int(v.y))

class Vec3I(_Vec234I):
    def __init__(self, name, value=Vector3I(0, 0, 0)):
        super(Vec3I, self).__init__(name)
        assert Vector3I is type(value)
        self._value = value

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert Vector3I is type(value)
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds()
        else:
            ds[idx_thread][path] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector3I(val[0], val[1], val[2])

    def _set_value(self, value):
        assert Vector3I is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        v = self._value
        return 'int32 %s[4] = %i,%i,%i,0\n' % (self.name, int(v.x), int(v.y), int(v.z))

class Vec4I(_Vec234I):
    def __init__(self, name, value=Vector4I(0, 0, 0, 0)):
        super(Vec3I, self).__init__(name)
        assert Vector4I is type(value)
        self._value = value

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert Vector4I is type(value)
        if idx_thread is None:
            for d in ds:
                d[path] = value.to_ds()
        else:
            ds[idx_thread][path] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path]
        else:
            val = ds[idx_thread][path]
        return Vector4I(val[0], val[1], val[2], val[3])

    def _set_value(self, value):
        assert Vector4I is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        v = self._value
        return 'int32 %s[4] = %i,%i,%i,%i\n' % (self.name, int(v.x), int(v.y), int(v.z), int(v.w))


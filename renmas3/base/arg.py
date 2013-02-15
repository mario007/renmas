import platform
import inspect
from .vector3 import Vector2, Vector3, Vector4
from .vector3 import Vector2I, Vector3I, Vector4I
from .spectrum import Spectrum, RGBSpectrum, SampledSpectrum
from .util import float2hex

def conv_int_to_float(cgen, reg, xmm):
    #TODO --- test that reg is general and xmm is xmm
    if cgen.AVX:
        return "vcvtsi2ss %s, %s, %s \n" % (xmm, xmm, reg)
    else:
        return "cvtsi2ss %s, %s \n" % (xmm, reg)

def conv_float_to_int(cgen, reg, xmm):
    #TODO --- test that reg is general and xmm is xmm
    if cgen.AVX:
        return "vcvttss2si %s, %s \n" % (reg, xmm)
    else:
        return "cvttss2si %s, %s \n" % (reg, xmm)

def check_ptr_reg(cgen, ptr_reg):
    if ptr_reg is None:
        raise ValueError("If vector is attribute register pointer is also required")

    if cgen.BIT64 and cgen.regs.is_reg32(ptr_reg):
        raise ValueError("Pointer register must be 64-bit!", ptr_reg)
    if not cgen.BIT64 and cgen.regs.is_reg64(ptr_reg):
        raise ValueError("Pointer register must be 32-bit!", ptr_reg)

def _copy_values_avx(cgen, src_reg, dst_reg, n, src_path, dst_path):
    def _load_xmms(offset, nregs):
        code = ''
        _xmm = ['ymm7', 'ymm6', 'ymm5', 'ymm4', 'ymm3', 'ymm2', 'ymm1', 'ymm0']
        xmms = []
        for i in range(nregs):
            xmm = _xmm.pop()
            code += "vmovaps %s, yword[%s + %s + %i] \n"  % (xmm, src_reg, src_path, offset)
            xmms.append(xmm)
            offset += 32
        return code, xmms

    def _store_xmms(xmms, offset):
        code = ''
        for xmm in xmms:
            code += "vmovaps yword[%s + %s + %i], %s\n"  % (dst_reg, dst_path, offset, xmm)
            offset += 32
        return code

    rounds = n // 8
    nrounds = 0
    code = ""
    while rounds > 0:
        nregs = 8 if rounds > 8 else rounds
        code1, xmms= _load_xmms(nrounds * 32, nregs)
        code2 = _store_xmms(xmms, nrounds * 32) 
        code += code1 + code2
        rounds -= 8
        nrounds += 8
    return code

def _copy_values_sse(cgen, src_reg, dst_reg, n, src_path, dst_path):
    def _load_xmms(offset, nregs):
        code = ''
        _xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        xmms = []
        for i in range(nregs):
            xmm = _xmm.pop()
            code += "movaps %s, oword[%s + %s + %i] \n"  % (xmm, src_reg, src_path, offset)
            xmms.append(xmm)
            offset += 16
        return code, xmms

    def _store_xmms(xmms, offset):
        code = ''
        for xmm in xmms:
            code += "movaps oword[%s + %s + %i], %s\n"  % (dst_reg, dst_path, offset, xmm)
            offset += 16
        return code

    rounds = n // 4
    nrounds = 0
    code = ""
    while rounds > 0:
        nregs = 8 if rounds > 8 else rounds
        code1, xmms= _load_xmms(nrounds * 16, nregs)
        code2 = _store_xmms(xmms, nrounds * 16) 
        code += code1 + code2
        rounds -= 8
        nrounds += 8
    return code

def copy_values(cgen, src_reg, dst_reg, n, src_path, dst_path):
    #NOTE n must be divisible by 8
    check_ptr_reg(cgen, src_reg)
    check_ptr_reg(cgen, dst_reg)
    if cgen.AVX:
        return _copy_values_avx(cgen, src_reg, dst_reg, n, src_path, dst_path)
    else:
        return _copy_values_sse(cgen, src_reg, dst_reg, n, src_path, dst_path)

class Argument:
    """
    Abstract base class that define interface for type in shading language.
    All supported types in shading language must inherit this class.
    """
    def __init__(self, name):
        """Name of the argument."""
        self.name = name

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        """Store number in data section."""
        raise NotImplementedError()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        """Load number form data section."""
        raise NotImplementedError()

    def generate_data(self):
        """Generate code for local variable in #DATA section."""
        raise NotImplementedError()

    @classmethod
    def load_cmd(cls, cgen, name, reg=None, path=None, ptr_reg=None, offset=None):
        """Generate code that load number from memory location to register."""
        raise NotImplementedError()

    @classmethod
    def store_cmd(cls, cgen, reg, name, path=None, ptr_reg=None, offset=None):
        """Generate code that store number from register to memory location."""
        raise NotImplementedError()

    @classmethod
    def neg_cmd(cls, cgen, reg):
        """Generate arightmetic code that negates number."""
        raise NotImplementedError()

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        """Generate code for arithmetic operation between registers."""
        raise NotImplementedError()

    @classmethod
    def rev_arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        """Generate code for arithmetic operation between registers."""
        raise NotImplementedError()

    @classmethod
    def supported(cls, operator, typ):
        """Return true if arithmetic with specified type is suppored."""
        raise NotImplementedError()

class Integer(Argument):

    def __init__(self, name, value=0):
        super(Integer, self).__init__(name)
        assert int is type(value)
        self._value = value

    def _set_value(self, value):
        assert int is type(value)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert int is type(value)
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

    def generate_data(self):
        return 'int32 %s = %i \n' % (self.name, self._value) 

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='general')

        tmp = dest_reg
        if cgen.regs.is_xmm(dest_reg):
            tmp = cgen.register(typ='general')
        code = "mov %s, dword [%s] \n" % (tmp, self.name)

        if not cgen.regs.is_xmm(dest_reg):
            return code, tmp, Integer

        # implicit conversion to float
        conversion = conv_int_to_float(cgen, tmp, dest_reg)
        cgen.release_reg(tmp)
        return code + conversion, dest_reg, Float

    def store_cmd(self, cgen, reg):
        return "mov dword [%s], %s \n" % (self.name, reg)

    def store_const(self, cgen, const):
        if not isinstance(const, int):
            raise ValueError("Integer constant is expected and got ", const)
        return'mov dword [%s], %i \n' % (self.name, const)

    @classmethod
    def store_attr_const(cls, cgen, path, ptr_reg, const):
        check_ptr_reg(cgen, ptr_reg)
        code = "mov dword [%s + %s], %i\n" % (ptr_reg, path, int(const))
        return code

    @classmethod
    def load_attr(cls, cgen, path, ptr_reg, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='general')

        tmp = dest_reg
        if cgen.regs.is_xmm(dest_reg):
            tmp = cgen.register(typ='general')
        check_ptr_reg(cgen, ptr_reg)
        code = "mov %s, dword [%s + %s]\n" % (tmp, ptr_reg, path)
        if not cgen.regs.is_xmm(dest_reg):
            return code, tmp, Integer

        # implicit conversion to float
        conversion = conv_int_to_float(cgen, tmp, dest_reg)
        cgen.release_reg(tmp)
        return code + conversion, dest_reg, Float

    @classmethod
    def store_attr(cls, cgen, path, ptr_reg, src_reg):
        check_ptr_reg(cgen, ptr_reg)
        return "mov dword [%s + %s], %s\n" % (ptr_reg, path, src_reg)

    @classmethod
    def neg_cmd(cls, cgen, reg):
        return 'neg %s\n' % reg

    @classmethod
    def supported(cls, operator, typ):
        if typ != Integer:
            return False
        if operator not in ('+', '-', '/', '*', '%'):
            return False
        return True

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)
        ops = {'+': 'add', '-': 'sub', '*': 'imul'}
        if operator in ops:
            code = '%s %s, %s\n' % (ops[operator], reg1, reg2)
        if operator == '%' or operator == '/': #TODO test 64-bit implementation is needed
            code, reg1 = Integer._arith_div(cgen, reg1, reg2, operator)
        return code, reg1, Integer

    @classmethod
    def _arith_div(cls, cgen, reg1, reg2, operator):
        epilog = """
        push eax
        push edx
        push esi
        """
        line1 = "mov eax, %s\n" % reg1
        line2 = "mov esi, %s\n" % reg2
        line3 = "xor edx, edx\n"
        line4 = "idiv esi\n"
        line5 = "pop esi\n"
        if operator == '/':
            line6 = "pop edx\n"
            line7 = "mov %s, eax\n" % reg1
            if reg1 == 'eax':
                line8 = "add esp, 4\n"
            else:
                line8 = "pop eax\n"
        else:
            line6 = "mov %s, edx\n" % reg1
            if reg1 == 'edx':
                line7 = "add esp, 4\n"
            else:
                line7 = "pop edx\n"
            if reg1 == 'eax':
                line8 = "add esp, 4\n"
            else:
                line8 = "pop eax\n"
        code = epilog + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
        return code, reg1

class Float(Argument):

    def __init__(self, name, value=0.0):
        super(Float, self).__init__(name)
        self._value = float(value)

    def _set_value(self, value):
        self._value = float(value)

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        if idx_thread is None:
            for d in ds:
                d[path] = float(value) 
        else:
            ds[idx_thread][path] = float(value)

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            return ds[0][path]
        else:
            return ds[idx_thread][path]

    def generate_data(self):
        return 'float %s = %f \n' % (self.name, self._value)

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)
        if cgen.AVX:
            code = "vmovss %s, dword [%s] \n" % (dest_reg, self.name)
        else:
            code = "movss %s, dword [%s] \n" % (dest_reg, self.name)
        return code, dest_reg, Float

    def store_cmd(self, cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!")
        if cgen.AVX:
            code = "vmovss dword [%s], %s \n" % (self.name, xmm)
        else:
            code = "movss dword [%s], %s \n" % (self.name, xmm)
        return code

    def store_const(self, cgen, const):
        fl = float2hex(float(const))
        return'mov dword [%s], %s ;float value = %f \n' % (self.name, fl, const)

    @classmethod
    def store_attr_const(cls, cgen, path, ptr_reg, const):
        fl = float2hex(float(const))
        check_ptr_reg(cgen, ptr_reg)
        code = "mov dword [%s + %s], %s ;float value = %f \n" % (ptr_reg, path, fl, const)
        return code

    @classmethod
    def load_attr(cls, cgen, path, ptr_reg, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        if not cgen.regs.is_xmm(dest_reg):
            raise ValueError("Destination register must be xmm register!", dest_reg)
        check_ptr_reg(cgen, ptr_reg)
        if cgen.AVX:
            code = "vmovss %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "movss %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, Float

    @classmethod
    def store_attr(cls, cgen, path, ptr_reg, xmm):
        check_ptr_reg(cgen, ptr_reg)
        if cgen.AVX:
            code = "vmovss dword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code = "movss dword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code

    @classmethod
    def neg_cmd(cls, cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)

        arg = cgen.create_const(-1.0)
        if cgen.AVX:
            code = "vmulss %s, %s, dword[%s]\n" % (xmm, xmm, arg.name) 
        else:
            code = "mulss %s, dword[%s]\n" % (xmm, arg.name) 
        return code

    @classmethod
    def supported(cls, operator, typ):
        if typ != Integer and typ != Float:
            return False
        if operator not in ('+', '-', '/', '*'):
            return False
        return True

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)

        code = ''
        xmm = reg2
        if typ2 == Integer:
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg2, xmm)
            cgen.release_reg(xmm)

        ops_avx = {'+': 'vaddss', '-': 'vsubss', '*': 'vmulss', '/': 'vdivss'}
        ops = {'+': 'addss', '-': 'subss', '*': 'mulss', '/': 'divss'}

        if cgen.AVX:
            code += "%s %s, %s, %s \n" % (ops_avx[operator], reg1, reg1, xmm)
        else:
            code += "%s %s, %s \n" % (ops[operator], reg1, xmm)
        return code, reg1, Float

    @classmethod
    def rev_arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)

        code = ''
        xmm = reg2
        if typ2 == Integer:
            xmm = cgen.register(typ="xmm")
            code += conv_int_to_float(cgen, reg2, xmm)
            cgen.release_reg(xmm)

        code3, reg3, typ3 = Float.arith_cmd(cgen, xmm, reg1, Float, operator)
        return code + code3, reg3, typ3

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
    def store_attr(cls, cgen, path, ptr_reg, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected!", xmm)
        check_ptr_reg(cgen, ptr_reg)
        if cgen.AVX:
            code = "vmovaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code = "movaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code

    def load_subscript(self, cgen, index, dest_reg=None):
        pass

    def store_subscript(self, cgen, index, src_reg):
        pass

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
            cgen.release_reg(xmm)

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

class _Vec234I(Argument):
    pass

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

class UserType:
    def __init__(self, typ):
        self._typ = typ
        self._args_lst = []
        self._args = {}

    @property
    def typ(self):
        return self._typ

    def add(self, arg):
        if arg.name in self._args:
            raise ValueError("Argument allready exist!", arg)
        self._args[arg.name] = arg
        self._args_lst.append(arg)

    def generate_paths(self, name):
        paths = {}
        for arg in self._args_lst:
            if isinstance(arg, Struct):
                #TODO not tested yet - struct inside struct
                for key, value in arg.paths.items():
                    paths[name + '.' + key] = value
            else:
                paths[name + '.' + arg.name] = arg
        return paths

    def generate_struct(self):
        code = "struct %s \n" % self._typ
        for a in self._args_lst:
            code += a.generate_data()
        code += "end struct \n\n"
        return code

class Struct(Argument):
    def __init__(self, name, typ):
        super(Struct, self).__init__(name)
        self._typ = typ
        self._paths = typ.generate_paths(name)

    @property
    def typ(self):
        return self._typ

    @property
    def paths(self):
        return self._paths

    def argument_exist(self, path): # path example: path = ps.x.y
        return path in self._paths

    def get_argument(self, path):
        if path in self._paths:
            return self._paths[path]
        return None

    def generate_data(self):
        return '%s %s\n' % (self._typ.typ, self.name)

    def set_value(self, ds, value, path, idx_thread=None):
        for p, arg in self._paths.items():
            obj = getattr(value, arg.name)
            if obj is None:
                continue
            arg.set_value(ds, obj, p, idx_thread)

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            if cgen.BIT64:
                dest_reg = cgen.register(typ='general', bit=64)
            else:
                dest_reg = cgen.register(typ='general', bit=32)
        check_ptr_reg(cgen, dest_reg)
        code = "mov %s, %s \n" % (dest_reg, self.name)
        return code, dest_reg, Struct

    def load_attr_cmd(self, cgen, path, dest_reg=None, ptr_reg=None):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen, ptr_reg)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2, src_reg2, type2 = arg.load_attr(cgen, asm_path, src_reg, dest_reg)
        if ptr_reg is None:
            cgen.release_reg(src_reg)

        return code1 + code2, src_reg2, type2 

    def store_attr_cmd(self, cgen, path, reg):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2 = arg.store_attr(cgen, asm_path, src_reg, reg)
        cgen.release_reg(src_reg)
        return code1 + code2

    def store_attr_const(self, cgen, path, const):
        arg = self.get_argument('%s.%s' % (self.name, path))
        if arg is None:
            raise ValueError("Argument %s doesn't exist in structure %s" % (path, self.name))
        code1, src_reg, type1 = self.load_cmd(cgen)

        asm_path = "%s.%s" %(self.typ.typ, path)
        code2 = arg.store_attr_const(cgen, asm_path, src_reg, const)

        cgen.release_reg(src_reg)
        return code1 + code2

class StructPtr(Struct):
    def generate_data(self):
        bits = platform.architecture()[0]
        if bits == '64bit':
            return 'uint64 %s\n' % self.name
        else:
            return 'uint32 %s\n' % self.name

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            if cgen.BIT64:
                dest_reg = cgen.register(typ='general', bit=64)
            else:
                dest_reg = cgen.register(typ='general', bit=32)
        check_ptr_reg(cgen, dest_reg)
        if cgen.BIT64:
            code = "mov %s, qword [%s] \n" % (dest_reg, self.name)
        else:
            code = "mov %s, dword [%s] \n" % (dest_reg, self.name)
        return code, dest_reg, StructPtr

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

class RGBSpec(Argument):
    def __init__(self, name, spectrum):
        super(RGBSpec, self).__init__(name)
        assert isinstance(spectrum, RGBSpectrum)
        self._value = spectrum

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            if cgen.BIT64:
                dest_reg = cgen.register(typ='general', bit=64)
            else:
                dest_reg = cgen.register(typ='general', bit=32)
        check_ptr_reg(cgen, dest_reg)
        code = "mov %s, %s \n" % (dest_reg, self.name)
        return code, dest_reg, RGBSpec

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
            code = "lea %s, qword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "lea %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, RGBSpec

    def store_cmd(self, cgen, reg):
        check_ptr_reg(cgen, reg)
        code = ''
        path = "Spectrum.values"
        code1, src_reg, typ1 = Vec4.load_attr(cgen, path, reg)
        code2, ptr_reg, typ2 = self.load_cmd(cgen)
        code3 = Vec4.store_attr(cgen, path, ptr_reg, src_reg)
        code = code1 + code2 + code3
        cgen.release_reg(src_reg)
        cgen.release_reg(ptr_reg)
        return code

    def _set_value(self, value):
        assert isinstance(value, RGBSpectrum)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        return 'Spectrum %s\n' % self.name

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert isinstance(value, RGBSpectrum)
        if idx_thread is None:
            for d in ds:
                ds[path + ".values"] = value.to_ds()
        else:
            ds[idx_thread][path + ".values"] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path + ".values"]
        else:
            val = ds[idx_thread][path + ".values"]
        return RGBSpectrum(val[0], val[1], val[2])

class SampledSpec(Argument):
    def __init__(self, name, spectrum):
        super(SampledSpec, self).__init__(name)
        assert isinstance(spectrum, SampledSpectrum)
        self._value = spectrum

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            if cgen.BIT64:
                dest_reg = cgen.register(typ='general', bit=64)
            else:
                dest_reg = cgen.register(typ='general', bit=32)
        check_ptr_reg(cgen, dest_reg)
        code = "mov %s, %s \n" % (dest_reg, self.name)
        return code, dest_reg, SampledSpec

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
            code = "lea %s, qword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "lea %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, SampledSpec

    def store_cmd(self, cgen, reg):
        check_ptr_reg(cgen, reg)
        code = ''
        path = "Spectrum.values"
        code1, dst_reg, typ1 = self.load_cmd(cgen)
        n = len(self._value.samples)
        code2 = copy_values(cgen, reg, dst_reg, n, path, path)
        cgen.release_reg(dst_reg)
        code = code1 + code2
        return code

    def _set_value(self, value):
        assert isinstance(value, SampledSpectrum)
        self._value = value

    def _get_value(self):
        return self._value
    value = property(_get_value, _set_value)

    def generate_data(self):
        return 'Spectrum %s\n' % self.name

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        assert isinstance(value, SampledSpectrum)
        if idx_thread is None:
            for d in ds:
                ds[path + ".values"] = value.to_ds()
        else:
            ds[idx_thread][path + ".values"] = value.to_ds()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        if idx_thread is None:
            val = ds[0][path + ".values"]
        else:
            val = ds[idx_thread][path + ".values"]
        return SampledSpectrum(val)

#TODO implement locking of map and list???-think
class ArgumentList:
    def __init__(self, args=[]):
        self._args = []
        for a in args:
            self._args.append(a)

    def __contains__(self, arg):
        return arg in self._args

    def __iter__(self):
        for a in self._args:
            yield a

    def __len__(self):
        return len(self._args)

class ArgumentMap:
    def __init__(self, args=[]):
        self._args = {}
        for a in args:
            self.add(a)

    def add(self, arg):
        if not isinstance(arg, Argument):
            raise ValueError("Wrong argument type", arg)

        if arg.name in self._args:
            raise ValueError("Argument %s allready exist", arg.name)
        self._args[arg.name] = arg

    def __contains__(self, name):
        return name in self._args

    def __getitem__(self, name):
        return self._args[name]

    def __iter__(self):
        for a in self._args.items():
            yield a

def arg_from_value(name, value, input_arg=False, spectrum=None):
    """Create argument based on type of value."""

    if isinstance(value, int):
        arg = Integer(name, value)
    elif isinstance(value, float):
        arg = Float(name, value)
    elif isinstance(value, tuple) or isinstance(value, list):
        if len(value) > 4:
            raise ValueError('Vector is to big!', value)
        if len(value) == 2:
            arg = Vec2(name, Vector2(float(value[0]), float(value[1])))
        elif len(value) == 3:
            arg = Vec3(name, Vector3(float(value[0]), float(value[1]), float(value[2])))
        elif len(value) == 4:
            arg = Vec4(name, Vector4(float(value[0]), float(value[1]),
                                     float(value[2]), float(value[3])))
        else:
            raise ValueError('Vector is to small!', value)
    elif isinstance(value, Vector2):
        arg = Vec2(name, value)
    elif isinstance(value, Vector3):
        arg = Vec3(name, value)
    elif isinstance(value, Vector4):
        arg = Vec4(name, value)
    elif isinstance(value, RGBSpectrum):
        arg = RGBSpec(name, value)
    elif isinstance(value, SampledSpectrum):
        arg = SampledSpec(name, value)
    elif isinstance(value, UserType):
        if input_arg:
            arg = StructPtr(name, value)
        else:
            arg = Struct(name, value)
    elif hasattr(type(value), 'user_type'):
        typ_name, fields = type(value).user_type()
        usr_type = create_user_type(typ_name, fields, spectrum=spectrum)
        if input_arg:
            arg = StructPtr(name, usr_type)
        else:
            arg = Struct(name, usr_type)
    else:
        raise ValueError('Unknown value type', value)
    return arg

def arg_from_type(name, typ, value=None, input_arg=False, spectrum=None):
    """Create argument of specified type."""

    if typ == Integer:
        val = 0 if value is None else int(value)
        arg = Integer(name, val)
    elif typ == Float:
        val = 0.0 if value is None else float(value)
        arg = Float(name, val)
    elif typ == Vec2:
        val = Vector2(0.0, 0.0) if value is None else value
        arg = Vec2(name, val)
    elif typ == Vec3:
        val = Vector3(0.0, 0.0, 0.0) if value is None else value
        arg = Vec3(name, val)
    elif typ == Vec4:
        val = Vector4(0.0, 0.0, 0.0, 0.0) if value is None else value
        arg = Vec4(name, val)
    elif typ == Vec2I:
        val = Vector2I(0, 0) if value is None else value
        arg = Vec2I(name, val)
    elif typ == Vec3I:
        val = Vector3I(0, 0, 0) if value is None else value
        arg = Vec3I(name, val)
    elif typ == Vec4I:
        val = Vector4I(0, 0, 0, 0) if value is None else value
        arg = Vec4I(name, val)
    elif typ == Pointer: #pointer in typ = UserType
        arg = Pointer(name, typ=value)
    elif typ == Spectrum:
        if value is None and spectrum is None:
            arg = RGBSpec(name, RGBSpectrum(0.0, 0.0, 0.0))
        elif isinstance(value, (RGBSpectrum, SampledSpectrum)):
            arg = RGBSpec(name, value)
        elif spectrum is not None:
            if isinstance(spectrum, RGBSpectrum):
                arg = RGBSpec(name, spectrum.black())
            elif isinstance(spectrum, SampledSpectrum):
                arg = SampledSpec(name, spectrum.black())
            else:
                raise ValueError("Unknown spectrum type!", typ)
        else:
            raise ValueError("Cannot create desired spectrum!", typ)
    elif hasattr(typ, 'user_type'):
        typ_name, fields = typ.user_type()
        usr_type = create_user_type(typ_name, fields, spectrum=spectrum)
        if input_arg:
            arg = StructPtr(name, usr_type)
        else:
            arg = Struct(name, usr_type)
    else:
        print (name, typ, value, spectrum)
        raise ValueError("Unknown type of arugment", typ)

    return arg

def create_argument(name, value=None, typ=None, input_arg=False, spectrum=None):
    """Factory for creating argument based on value or based on type."""

    if value is None and typ is None:
        raise ValueError("Argument could not be created because type and value is None.")

    if typ is not None:
        return arg_from_type(name, typ, value, input_arg, spectrum=spectrum)

    return arg_from_value(name, value, input_arg, spectrum=spectrum)


#a5 = create_user_type_(typ="point", fields=[('x', 55)])
def create_user_type(typ, fields, spectrum=None):
    usr_type = UserType(typ)
    for n, v in fields:
        if inspect.isclass(v):
            arg = create_argument(n, typ=v, spectrum=spectrum)
        else:
            arg = create_argument(n, value=v, spectrum=spectrum)
        usr_type.add(arg)
    return usr_type

class Attribute:
    def __init__(self, name, path):
        self.name = name #name of struct
        self.path = path #path to member in struct

class Callable:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Operations:
    def __init__(self, operations):
        self.operations = operations

class Const:
    def __init__(self, const):
        self.const = const

class Name:
    def __init__(self, name):
        self.name = name

class Subscript:
    def __init__(self, name, index, path=None):
        self.name = name
        self.index = index
        #if we have path than this is array in struct
        self.path = path #path to member in struct

class EmptyOperand:
    pass

class Operation:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


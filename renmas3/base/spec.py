
from .arg import Argument, conv_int_to_float, check_ptr_reg
from .integer import Integer, Float
from .vec234 import Vec4
from .spectrum import RGBSpectrum, SampledSpectrum

def _load_xmms(cgen, offset, nregs, reg, path, ignore=[]):
    if cgen.AVX:
        code = ''
        _xmm = ['ymm7', 'ymm6', 'ymm5', 'ymm4', 'ymm3', 'ymm2', 'ymm1', 'ymm0']
        for r in ignore:
            _xmm.remove(r)
        xmms = []
        for i in range(nregs):
            xmm = _xmm.pop()
            code += "vmovaps %s, yword[%s + %s + %i] \n"  % (xmm, reg, path, offset)
            xmms.append(xmm)
            offset += 32
        return code, xmms
    else:
        code = ''
        _xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        for r in ignore:
            _xmm.remove(r)
        xmms = []
        for i in range(nregs):
            xmm = _xmm.pop()
            code += "movaps %s, oword[%s + %s + %i] \n"  % (xmm, reg, path, offset)
            xmms.append(xmm)
            offset += 16
        return code, xmms

def _store_xmms(cgen, xmms, offset, reg, path):
    if cgen.AVX:
        code = ''
        for xmm in xmms:
            code += "vmovaps yword[%s + %s + %i], %s\n"  % (reg, path, offset, xmm)
            offset += 32
        return code
    else:
        code = ''
        for xmm in xmms:
            code += "movaps oword[%s + %s + %i], %s\n"  % (reg, path, offset, xmm)
            offset += 16
        return code

def _arithmetic(cgen, xmms, offset, reg, path, operator):
    if cgen.AVX:
        ops = {'+': 'vaddps', '-': 'vsubps', '*': 'vmulps', '/': 'vdivps'}
        code = ''
        for xmm in xmms:
            code += "%s %s, %s, yword[%s + %s + %i]\n"  % (ops[operator], xmm, xmm, reg, path, offset)
            offset += 32
        return code
    else:
        ops = {'+': 'addps', '-': 'subps', '*': 'mulps', '/': 'divps'}
        code = ''
        for xmm in xmms:
            code += "%s %s, oword[%s + %s + %i]\n"  % (ops[operator], xmm, reg, path, offset)
            offset += 16 
        return code

def copy_values(cgen, src_reg, dst_reg, n, src_path, dst_path):
    #NOTE n must be divisible by 8

    if cgen.AVX:
        rounds, WIDTH = n // 8, 32 
    else:
        rounds, WIDTH = n // 4, 16  
    nrounds = 0
    code = ""
    path = "Spectrum.values"
    while rounds > 0:
        nregs = 8 if rounds > 8 else rounds
        code1, xmms= _load_xmms(cgen, nrounds * WIDTH, nregs, src_reg, src_path)
        code2 = _store_xmms(cgen, xmms, nrounds * WIDTH, dst_reg, dst_path) 
        code += code1 + code2
        rounds -= 8
        nrounds += 8
    return code

def arith_sampled(cgen, src1, src2, dst, n, operator):

    if cgen.AVX:
        rounds, WIDTH = n // 8, 32 
    else:
        rounds, WIDTH = n // 4, 16  
    nrounds = 0
    code = ""
    path = "Spectrum.values"
    while rounds > 0:
        nregs = 8 if rounds > 8 else rounds
        code1, xmms= _load_xmms(cgen, nrounds * WIDTH, nregs, src1, path)
        code2 = _arithmetic(cgen, xmms, nrounds * WIDTH, src2, path, operator)
        code3 = _store_xmms(cgen, xmms, nrounds * WIDTH, dst, path) 
        code += code1 + code2 + code3
        rounds -= 8
        nrounds += 8
    return code

def arith_sampled_mult(cgen, src, dst, xmm, n): # '*' implied
    def _arithmetic(xmms, src_xmm):
        code = ''
        if cgen.AVX:
            for xmm in xmms:
                code += "vmulps %s, %s, %s\n" % (xmm, xmm, src_xmm)
            return code
        else:
            for xmm in xmms:
                code += "mulps %s, %s\n" % (xmm, src_xmm)
            return code

    if cgen.AVX:
        rounds, WIDTH = n // 8, 32 
    else:
        rounds, WIDTH = n // 4, 16  
    nrounds = 0
    code = ""
    path = "Spectrum.values"
    if cgen.AVX:
        xmm = "y" + xmm[1:]
        code += "vperm2f128 %s, %s, %s, 0x00 \n" % (xmm, xmm, xmm)
    while rounds > 0:
        nregs = 7 if rounds > 7 else rounds
        code1, xmms= _load_xmms(cgen, nrounds * WIDTH, nregs, src, path, [xmm])
        code2 = _arithmetic(xmms, xmm)
        code3 = _store_xmms(cgen, xmms, nrounds * WIDTH, dst, path) 
        code += code1 + code2 + code3
        rounds -= 7
        nrounds += 7
    return code

class RGBSpec(Argument):
    def __init__(self, name, spectrum):
        super(RGBSpec, self).__init__(name)
        assert isinstance(spectrum, RGBSpectrum)
        self._value = spectrum

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        check_ptr_reg(cgen, dest_reg)
        code = "mov %s, %s \n" % (dest_reg, self.name)
        return code, dest_reg, RGBSpec

    @classmethod
    def load_attr(cls, cgen, path, ptr_reg, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        check_ptr_reg(cgen, ptr_reg)
        check_ptr_reg(cgen, dest_reg)
        if cgen.BIT64:
            code = "lea %s, qword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "lea %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, RGBSpec

    def store_cmd(self, cgen, reg):
        check_ptr_reg(cgen, reg)
        path = "Spectrum.values"
        code1, src_reg, typ1 = Vec4.load_attr(cgen, path, reg)
        code2, ptr_reg, typ2 = self.load_cmd(cgen)
        code3 = Vec4.store_attr(cgen, path, ptr_reg, src_reg)
        code = code1 + code2 + code3
        cgen.release_reg(src_reg)
        cgen.release_reg(ptr_reg)
        return code

    @classmethod
    def store_attr(cls, cgen, path, ptr_reg, reg):
        check_ptr_reg(cgen, ptr_reg)
        check_ptr_reg(cgen, reg)

        path1 = "Spectrum.values"
        code1, src_reg, typ1 = Vec4.load_attr(cgen, path1, reg)
        path2 = path + ".values"
        code2 = Vec4.store_attr(cgen, path2, ptr_reg, src_reg)
        cgen.release_reg(src_reg)
        return code1 + code2

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

    @classmethod
    def supported(cls, operator, typ):
        if operator == '*':
            if typ == Integer or typ == Float or typ == cls:
                return True
        if operator not in ('+', '-', '/', '*'):
            return False
        if typ != RGBSpec:
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
    def _arith_cmd(cls, cgen, reg1, reg2, typ2, operator, swap=False):
        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)
        check_ptr_reg(cgen, reg1)

        path = "Spectrum.values"
        code1, xmm1, dummy = Vec4.load_attr(cgen, path, reg1)
        if typ2 == Integer or typ2 == Float:
            code2, xmm2 = cls._conv(cgen, reg2, typ2, operator)
        else:
            code2, xmm2, dummy = Vec4.load_attr(cgen, path, reg2)

        ops_avx = {'+': 'vaddps', '-': 'vsubps', '*': 'vmulps', '/': 'vdivps'}
        ops = {'+': 'addps', '-': 'subps', '*': 'mulps', '/': 'divps'}
        if swap:
            xmm1, xmm2 = xmm2, xmm1
        if cgen.AVX:
            code3 = "%s %s, %s, %s \n" % (ops_avx[operator], xmm1, xmm1, xmm2)
        else:
            code3 = "%s %s, %s \n" % (ops[operator], xmm1, xmm2)
        tmp_arg = cgen.create_tmp_spec()
        code4, reg3, typ3 = tmp_arg.load_cmd(cgen)
        code5 = Vec4.store_attr(cgen, path, reg3, xmm1)
        code = code1 + code2 + code3 + code4 + code5

        #relase locally alocated registers
        if swap:
            cgen.release_reg(xmm2)
            if typ2 == cls or reg2 != xmm1:
                cgen.release_reg(xmm1)
        else:
            cgen.release_reg(xmm1)
            if typ2 == cls or reg2 != xmm2:
                cgen.release_reg(xmm2)

        return code, reg3, RGBSpec

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        return cls._arith_cmd(cgen, reg1, reg2, typ2, operator, False)

    @classmethod
    def rev_arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        return cls._arith_cmd(cgen, reg1, reg2, typ2, operator, True)

    @classmethod
    def register_type(cls):
        return 'pointer'

class SampledSpec(Argument):
    def __init__(self, name, spectrum):
        super(SampledSpec, self).__init__(name)
        assert isinstance(spectrum, SampledSpectrum)
        self._value = spectrum

    def load_cmd(self, cgen, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        check_ptr_reg(cgen, dest_reg)
        code = "mov %s, %s \n" % (dest_reg, self.name)
        return code, dest_reg, SampledSpec

    @classmethod
    def load_attr(cls, cgen, path, ptr_reg, dest_reg=None):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        check_ptr_reg(cgen, ptr_reg)
        check_ptr_reg(cgen, dest_reg)
        if cgen.BIT64:
            code = "lea %s, qword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code = "lea %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code, dest_reg, SampledSpec

    def store_cmd(self, cgen, reg):
        check_ptr_reg(cgen, reg)
        path = "Spectrum.values"
        code1, dst_reg, typ1 = self.load_cmd(cgen)
        n = len(self._value.samples)
        code2 = copy_values(cgen, reg, dst_reg, n, path, path)
        cgen.release_reg(dst_reg)
        code = code1 + code2
        return code

    @classmethod
    def store_attr(cls, cgen, path, ptr_reg, reg):
        check_ptr_reg(cgen, ptr_reg)
        check_ptr_reg(cgen, reg)

        src_path = "Spectrum.values"
        dst_path = path + ".values"
        n = cgen.nsamples()
        code = copy_values(cgen, reg, ptr_reg, n, src_path, dst_path)
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

    @classmethod
    def supported(cls, operator, typ):
        if operator == '*':
            if typ == Integer or typ == Float or typ == cls:
                return True
        if operator not in ('+', '-', '/', '*'):
            return False
        if typ != SampledSpec:
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
                #TODO ymm registar not just xmm for SampledSpec
            else:
                code += "shufps %s, %s, 0x00\n" % (xmm, xmm)
        return code, xmm

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if not cls.supported(operator, typ2):
            raise ValueError('This type or arithmetic operation is not allowed', typ2, operator)
        check_ptr_reg(cgen, reg1)

        tmp_arg = cgen.create_tmp_spec()
        n = len(tmp_arg.value.samples)
        code, reg3, typ3 = tmp_arg.load_cmd(cgen)
        if typ2 == Integer or typ2 == Float:
            code2, xmm = cls._conv(cgen, reg2, typ2, operator)
            code3 = arith_sampled_mult(cgen, reg1, reg3, xmm, n) # '*' implied
            if xmm != reg2:
                cgen.release_reg(xmm)
            code = code + code2 + code3
            return code, reg3, SampledSpec
        else:
            code2 = arith_sampled(cgen, reg1, reg2, reg3, n, operator)
            return code + code2, reg3, SampledSpec

    @classmethod
    def rev_arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        if typ2 == cls:
            return SampledSpec.arith_cmd(cgen, reg2, reg1, typ2, operator)
        #NOTE we can do this because for integer and float only '*' is defined
        return SampledSpec.arith_cmd(cgen, reg1, reg2, typ2, operator)

    @classmethod
    def register_type(cls):
        return 'pointer'


from .util import float2hex
from .arg import Argument, conv_int_to_float, check_ptr_reg

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
        if operator == '%' or operator == '/':
            code, reg1 = Integer._arith_div(cgen, reg1, reg2, operator)
        return code, reg1, Integer

    @classmethod
    def _arith_div(cls, cgen, reg1, reg2, operator):
        if cgen.BIT64:
            return cls._arith_div64(cgen, reg1, reg2, operator)
        else:
            return cls._arith_div32(cgen, reg1, reg2, operator)


    @classmethod
    def _arith_div64(cls, cgen, reg1, reg2, operator):
        epilog = """
        push rax
        push rdx
        push rsi
        """
        line1 = "mov eax, %s\n" % reg1
        line2 = "mov esi, %s\n" % reg2
        line3 = "xor edx, edx\n"
        line4 = "idiv esi\n"
        line5 = "pop rsi\n"
        if operator == '/':
            line6 = "pop rdx\n"
            line7 = "mov %s, eax\n" % reg1
            if reg1 == 'eax':
                line8 = "add rsp, 8\n"
            else:
                line8 = "pop rax\n"
        else:
            line6 = "mov %s, edx\n" % reg1
            if reg1 == 'edx':
                line7 = "add rsp, 8\n"
            else:
                line7 = "pop rdx\n"
            if reg1 == 'eax':
                line8 = "add rsp, 8\n"
            else:
                line8 = "pop rax\n"
        code = epilog + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
        return code, reg1

    @classmethod
    def _arith_div32(cls, cgen, reg1, reg2, operator):
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

        code3, reg3, typ3 = Float.arith_cmd(cgen, xmm, reg1, Float, operator)
        return code + code3, reg3, typ3


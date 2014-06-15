
from .utils import float2hex
from .strs import Attribute, Name, Callable, Const, Subscript, Operations, NoOp
from .args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg,\
    StructArg, StructArgPtr, PointerArg, RGBArg, SampledArg, SampledArgPtr
from .arr import ArrayArg, ObjArray, PtrsArray


def conv_int_to_float(cgen, reg, xmm):
    if not cgen.regs.is_xmm(xmm):
        raise ValueError("xmm register is expected not %s" % xmm)
    if not cgen.regs.is_reg32(reg):
        raise ValueError("reg32 register is expected not %s" % reg)
    if cgen.AVX:
        return "vcvtsi2ss %s, %s, %s \n" % (xmm, xmm, reg)
    else:
        return "cvtsi2ss %s, %s \n" % (xmm, reg)


def conv_float_to_int(cgen, reg, xmm):
    if not cgen.regs.is_xmm(xmm):
        raise ValueError("xmm register is expected not %s" % xmm)
    if not cgen.regs.is_reg32(reg):
        raise ValueError("reg32 register is expected not %s" % reg)
    if cgen.AVX:
        return "vcvttss2si %s, %s \n" % (reg, xmm)
    else:
        return "cvttss2si %s, %s \n" % (reg, xmm)


def load_struct_ptr(cgen, operand):
    arg = cgen.get_arg(operand)
    ptr_reg = cgen.register(typ='pointer')
    if isinstance(arg, StructArgPtr):
        if cgen.BIT64:
            code = "mov %s, qword [%s] \n" % (ptr_reg, arg.name)
        else:
            code = "mov %s, dword [%s] \n" % (ptr_reg, arg.name)
    else:
        code = "mov %s, %s \n" % (ptr_reg, arg.name)
    path = "%s.%s" % (arg.type_name, operand.path)
    return code, ptr_reg, path


def _load_xmms(cgen, offset, nregs, reg):
    code = ''
    xmms = []
    if cgen.AVX:
        _xmm = ['ymm7', 'ymm6', 'ymm5', 'ymm4', 'ymm3', 'ymm2', 'ymm1', 'ymm0']
        for i in range(nregs):
            xmm = _xmm.pop()
            code += "vmovaps %s, yword[%s + %i] \n" % (xmm, reg, offset)
            xmms.append(xmm)
            offset += 32
    else:
        _xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        for i in range(nregs):
            xmm = _xmm.pop()
            code += "movaps %s, oword[%s + %i] \n" % (xmm, reg, offset)
            xmms.append(xmm)
            offset += 16
    return code, xmms


def _arithmetic(cgen, xmms, offset, reg, op):
    code = ''
    if cgen.AVX:
        ops = {'+': 'vaddps', '-': 'vsubps', '*': 'vmulps', '/': 'vdivps'}
        for xmm in xmms:
            code += "%s %s, %s, yword[%s + %i]\n" % (ops[op], xmm, xmm, reg, offset)
            offset += 32
    else:
        ops = {'+': 'addps', '-': 'subps', '*': 'mulps', '/': 'divps'}
        for xmm in xmms:
            code += "%s %s, oword[%s + %i]\n" % (ops[op], xmm, reg, offset)
            offset += 16
    return code


def _store_xmms(cgen, xmms, offset, reg):
    code = ''
    if cgen.AVX:
        for xmm in xmms:
            code += "vmovaps yword[%s + %i], %s\n" % (reg, offset, xmm)
            offset += 32
    else:
        for xmm in xmms:
            code += "movaps oword[%s + %i], %s\n" % (reg, offset, xmm)
            offset += 16
    return code


def arithmetic_sampled(cgen, reg1, op, reg2, dst_reg, n):

    if cgen.AVX:
        rounds, WIDTH = n // 8, 32
    else:
        rounds, WIDTH = n // 4, 16

    nrounds = 0
    code = ""
    while rounds > 0:
        nregs = 8 if rounds > 8 else rounds
        code1, xmms = _load_xmms(cgen, nrounds * WIDTH, nregs, reg1)
        code2 = _arithmetic(cgen, xmms, nrounds * WIDTH, reg2, op)
        code3 = _store_xmms(cgen, xmms, nrounds * WIDTH, dst_reg)
        code += code1 + code2 + code3
        rounds -= 8
        nrounds += 8
    return code


def arith_sampled_mult(cgen, reg1, dst_reg, n):  # '*' and xmm7 implied
    def _arithmetic_mult(xmms):
        code = ''
        if cgen.AVX:
            for xmm in xmms:
                code += "vmulps %s, %s, %s\n" % (xmm, xmm, 'ymm7')
        else:
            for xmm in xmms:
                code += "mulps %s, %s\n" % (xmm, 'xmm7')
        return code

    if cgen.AVX:
        rounds, WIDTH = n // 8, 32
    else:
        rounds, WIDTH = n // 4, 16

    nrounds = 0
    code = ""

    while rounds > 0:
        nregs = 7 if rounds > 7 else rounds
        code1, xmms = _load_xmms(cgen, nrounds * WIDTH, nregs, reg1)
        code2 = _arithmetic_mult(xmms)
        code3 = _store_xmms(cgen, xmms, nrounds * WIDTH, dst_reg)
        code += code1 + code2 + code3
        rounds -= 7
        nrounds += 7
    return code


def store_const(cgen, dest, const):
    def _store_int_name_const(cgen, dest, const, arg):
        return'mov dword [%s], %i \n' % (arg.name, const)

    def _store_float_name_const(cgen, dest, const, arg):
        fl = float2hex(const)
        return'mov dword [%s], %s ;float value = %f \n' % (arg.name, fl, const)

    def _store_vec2_name_const(cgen, dest, const, arg):
        x, y = float(const[0]), float(const[1])
        fl1, fl2 = float2hex(x), float2hex(y)
        code = 'mov dword [%s], %s ;value = %f \n' % (arg.name, fl1, x)
        code += 'mov dword [%s + 4], %s ;value = %f \n' % (arg.name, fl2, y)
        return code

    def _store_vec3_name_const(cgen, dest, const, arg):
        x, y, z = float(const[0]), float(const[1]), float(const[2])
        fl1, fl2, fl3 = float2hex(x), float2hex(y), float2hex(z)
        code = 'mov dword [%s], %s ;value = %f \n' % (arg.name, fl1, x)
        code += 'mov dword [%s + 4], %s ;value = %f \n' % (arg.name, fl2, y)
        code += 'mov dword [%s + 8], %s ;value = %f \n' % (arg.name, fl3, z)
        return code

    def _store_vec4_name_const(cgen, dest, const, arg):
        x, y = float(const[0]), float(const[1])
        z, w = float(const[2]), float(const[3])
        f1, f2, f3, f4 = float2hex(x), float2hex(y), float2hex(z), float2hex(w)
        code = 'mov dword [%s], %s ;value = %f \n' % (arg.name, f1, x)
        code += 'mov dword [%s + 4], %s ;value = %f \n' % (arg.name, f2, y)
        code += 'mov dword [%s + 8], %s ;value = %f \n' % (arg.name, f3, z)
        code += 'mov dword [%s + 12], %s ;value = %f \n' % (arg.name, f4, w)
        return code

    def _store_int_atr_const(cgen, dest, const, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        code += "mov dword [%s + %s], %i\n" % (ptr_reg, path, const)
        return code

    def _store_float_atr_const(cgen, dest, const, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        fl = float2hex(float(const))
        code += "mov dword [%s + %s], %s ;%f \n" % (ptr_reg, path, fl, const)
        return code

    def _store_vec2_atr_const(cgen, dest, const, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        fl = float2hex(float(const[0]))
        c = "mov dword [%s + %s], %s ;%f\n" % (ptr_reg, path, fl, const[0])
        fl = float2hex(float(const[1]))
        d = "mov dword [%s + %s + 4], %s ;%f\n" % (ptr_reg, path, fl, const[1])
        return code + c + d

    def _store_vec3_atr_const(cgen, dest, const, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        f = float2hex(float(const[0]))
        c = "mov dword [%s + %s], %s ;%f \n" % (ptr_reg, path, f, const[0])
        f = float2hex(float(const[1]))
        d = "mov dword [%s + %s + 4], %s ;%f\n" % (ptr_reg, path, f, const[1])
        f = float2hex(float(const[2]))
        k = "mov dword [%s + %s + 8], %s ;%f\n" % (ptr_reg, path, f, const[2])
        return code + c + d + k

    def _store_vec4_atr_const(cgen, dest, const, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        f = float2hex(float(const[0]))
        c = "mov dword [%s + %s], %s ;%f \n" % (ptr_reg, path, f, const[0])
        f = float2hex(float(const[1]))
        d = "mov dword [%s + %s + 4], %s ;%f \n" % (ptr_reg, path, f, const[1])
        f = float2hex(float(const[2]))
        k = "mov dword [%s + %s + 8], %s ;%f \n" % (ptr_reg, path, f, const[2])
        f = float2hex(float(const[3]))
        m = "mov dword [%s + %s + 12], %s ;%f\n" % (ptr_reg, path, f, const[3])
        return code + c + d + k + m

    _stf = {(Name, IntArg): _store_int_name_const,
            (Name, FloatArg): _store_float_name_const,
            (Name, Vec2Arg): _store_vec2_name_const,
            (Name, Vec3Arg): _store_vec2_name_const,
            (Name, Vec4Arg): _store_vec2_name_const,
            (Attribute, IntArg): _store_int_atr_const,
            (Attribute, FloatArg): _store_float_atr_const,
            (Attribute, Vec2Arg): _store_vec2_atr_const,
            (Attribute, Vec3Arg): _store_vec3_atr_const,
            (Attribute, Vec4Arg): _store_vec4_atr_const,
            }

    arg = cgen.create_arg(dest, const)
    if isinstance(dest, (Name, Attribute, Subscript)):
        key = (type(dest), type(arg))
        if key not in _stf:
            raise ValueError("Store const fials! Missing store method.", key)
        code = _stf[key](cgen, dest, const.const, arg)
        return code
    raise ValueError("Store const, unsuported destination!", dest)


def _load_avx_samples(n, offset, name):
    x1 = ['ymm7', 'ymm6', 'ymm5', 'ymm4',
          'ymm3', 'ymm2', 'ymm1', 'ymm0']
    xmms = []
    code = ''
    for i in range(n):
        xmm = x1.pop()
        code += "vmovaps %s, yword [%s + %i]\n" % (xmm, name, offset)
        offset += 32
        xmms.append(xmm)
    return code, xmms


def _load_sse_samples(n, offset, name):
    x1 = ['xmm7', 'xmm6', 'xmm5', 'xmm4',
          'xmm3', 'xmm2', 'xmm1', 'xmm0']
    xmms = []
    code = ''
    for i in range(n):
        xmm = x1.pop()
        code += "movaps %s, oword [%s + %i]\n" % (xmm, name, offset)
        offset += 16
        xmms.append(xmm)
    return code, xmms


def _store_samples(offset, name, xmms, cgen):
    code = ''
    for xmm in xmms:
        if cgen.AVX:
            code += "vmovaps yword [%s + %i], %s \n" % (name, offset, xmm)
            offset += 32
        else:
            code += "movaps oword [%s + %i], %s \n" % (name, offset, xmm)
            offset += 16
    return code


def _store_samples_attr(offset, reg, path, xmms, cgen):
    code = ''
    for xmm in xmms:
        if cgen.AVX:
            code += "vmovaps yword [%s + %s + %i], %s \n" % (reg, path, offset, xmm)
            offset += 32
        else:
            code += "movaps oword [%s + %s + %i], %s \n" % (reg, path, offset, xmm)
            offset += 16
    return code


def store_operand(cgen, dest, reg, typ):

    def _store_int_name_arg(cgen, dest, reg, arg):
        return "mov dword [%s], %s \n" % (arg.name, reg)

    def _store_float_name_arg(cgen, dest, xmm, arg):
        if cgen.AVX:
            code = "vmovss dword [%s], %s \n" % (arg.name, xmm)
        else:
            code = "movss dword [%s], %s \n" % (arg.name, xmm)
        return code

    def _store_vec234_name_arg(cgen, dest, xmm, arg):
        if cgen.AVX:
            code = "vmovaps oword [%s], %s \n" % (arg.name, xmm)
        else:
            code = "movaps oword [%s], %s \n" % (arg.name, xmm)
        return code

    def _store_rgb_name_arg(cgen, dest, xmm, arg):
        if cgen.AVX:
            code = "vmovaps oword [%s], %s \n" % (arg.name, xmm)
        else:
            code = "movaps oword [%s], %s \n" % (arg.name, xmm)
        return code

    def _store_sampled_name_arg(cgen, dest, reg, arg):
        used_xmms = cgen.get_used_xmms()
        prolog = cgen.save_regs(used_xmms)

        width = 8 if cgen.AVX else 4
        rounds = len(arg.value.samples) // width

        code = ''
        offset = 0
        while rounds > 0:
            n = 8 if rounds > 8 else rounds
            if cgen.AVX:
                code1, xmms = _load_avx_samples(n, offset, reg)
                code2 = _store_samples(offset, arg.name, xmms, cgen)
                offset += n * 32
            else:
                code1, xmms = _load_sse_samples(n, offset, reg)
                code2 = _store_samples(offset, arg.name, xmms, cgen)
                offset += n * 16
            rounds -= 8
            code += code1 + code2
        epilog = cgen.load_regs(used_xmms)
        return prolog + code + epilog

    def _store_atr_sampled_arg(cgen, dest, reg, arg):
        used_xmms = cgen.get_used_xmms()
        prolog = cgen.save_regs(used_xmms)

        ld_struct, ptr_reg, path = load_struct_ptr(cgen, dest)

        width = 8 if cgen.AVX else 4
        rounds = len(arg.value.samples) // width
        code = ''
        offset = 0
        while rounds > 0:
            n = 8 if rounds > 8 else rounds
            if cgen.AVX:
                code1, xmms = _load_avx_samples(n, offset, reg)
                code2 = _store_samples_attr(offset, ptr_reg, path, xmms, cgen)
                offset += n * 32
            else:
                code1, xmms = _load_sse_samples(n, offset, reg)
                code2 = _store_samples_attr(offset, ptr_reg, path, xmms, cgen)
                offset += n * 16
            rounds -= 8
            code += code1 + code2
        epilog = cgen.load_regs(used_xmms)
        return prolog + ld_struct + code + epilog

    def _store_atr_int_arg(cgen, dest, reg, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        code += "mov dword [%s + %s], %s\n" % (ptr_reg, path, reg)
        return code

    def _store_atr_flt_arg(cgen, dest, xmm, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        if cgen.AVX:
            code += "vmovss dword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code += "movss dword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code

    def _store_atr_vec234_arg(cgen, dest, xmm, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        if cgen.AVX:
            code2 = "vmovaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code2 = "movaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code + code2

    def _store_atr_rgb_arg(cgen, dest, xmm, arg):
        code, ptr_reg, path = load_struct_ptr(cgen, dest)
        if cgen.AVX:
            code2 = "vmovaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        else:
            code2 = "movaps oword [%s + %s], %s\n" % (ptr_reg, path, xmm)
        return code + code2

    def _store_name_struct_arg(cgen, dest, reg, arg):
        if cgen.BIT64:
            return "mov qword [%s], %s \n" % (arg.name, reg)
        else:
            return "mov dword [%s], %s \n" % (arg.name, reg)

    def _store_name_pointer_arg(cgen, dest, reg, arg):
        if cgen.BIT64:
            return "mov qword [%s], %s \n" % (arg.name, reg)
        else:
            return "mov dword [%s], %s \n" % (arg.name, reg)

    _stf = {(Name, IntArg): _store_int_name_arg,
            (Name, FloatArg): _store_float_name_arg,
            (Name, Vec2Arg): _store_vec234_name_arg,
            (Name, Vec3Arg): _store_vec234_name_arg,
            (Name, Vec4Arg): _store_vec234_name_arg,
            (Name, RGBArg): _store_rgb_name_arg,
            (Name, SampledArg): _store_sampled_name_arg,
            (Attribute, IntArg): _store_atr_int_arg,
            (Attribute, FloatArg): _store_atr_flt_arg,
            (Attribute, Vec2Arg): _store_atr_vec234_arg,
            (Attribute, Vec3Arg): _store_atr_vec234_arg,
            (Attribute, Vec4Arg): _store_atr_vec234_arg,
            (Attribute, RGBArg): _store_atr_rgb_arg,
            (Attribute, SampledArg): _store_atr_sampled_arg,
            (Name, StructArgPtr): _store_name_struct_arg,
            (Name, PointerArg): _store_name_pointer_arg
            }

    #TODO -- implict conversion int to float
    arg = cgen.create_arg(dest, typ)
    key = (type(dest), type(arg))
    if key not in _stf:
        raise ValueError("Store operand fials! Missing store method.", key)
    code = _stf[key](cgen, dest, reg, arg)
    return code


def load_operand(cgen, op, dest_reg=None):

    def _general(dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='general')
        return dest_reg

    def _xmm(dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        return dest_reg

    def _pointer(dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        return dest_reg

    def _check_xmm(cgen, xmm):
        if not cgen.regs.is_xmm(xmm):
            raise ValueError("xmm register is expected not %s" % xmm)

    def _load_int_name_arg(cgen, op, arg, dest_reg):
        reg = _general(dest_reg)
        if cgen.regs.is_reg32(reg):
            code = "mov %s, dword [%s] \n" % (reg, arg.name)
            return code, reg, IntArg

        #Note: if destination is xmm we want implicit conversion to float
        tmp = cgen.register(typ='general')
        code = "mov %s, dword [%s] \n" % (tmp, arg.name)
        _check_xmm(cgen, reg)
        conv = conv_int_to_float(cgen, tmp, reg)
        cgen.release_reg(tmp)
        return code + conv, reg, FloatArg

    def _load_float_name_arg(cgen, op, arg, dest_reg):
        xmm = _xmm(dest_reg)
        _check_xmm(cgen, xmm)
        if cgen.AVX:
            code = "vmovss %s, dword [%s] \n" % (xmm, arg.name)
        else:
            code = "movss %s, dword [%s] \n" % (xmm, arg.name)
        return code, xmm, FloatArg

    def _load_vec234_name_arg(cgen, op, arg, dest_reg):
        xmm = _xmm(dest_reg)
        _check_xmm(cgen, xmm)
        if cgen.AVX:
            code = "vmovaps %s, oword [%s] \n" % (xmm, arg.name)
        else:
            code = "movaps %s, oword [%s] \n" % (xmm, arg.name)
        return code, xmm, type(arg)

    def _load_rgb_name_arg(cgen, op, arg, dest_reg):
        xmm = _xmm(dest_reg)
        _check_xmm(cgen, xmm)
        if cgen.AVX:
            code = "vmovaps %s, oword [%s] \n" % (xmm, arg.name)
        else:
            code = "movaps %s, oword [%s] \n" % (xmm, arg.name)
        return code, xmm, RGBArg

    def _load_sampled_name_arg(cgen, op, arg, dest_reg):
        reg = _pointer(dest_reg)
        #TODO check if reg is valid 32-64 bit pointer
        code = 'mov %s, %s\n' % (reg, arg.name)
        return code, reg, SampledArg

    def _load_atr_sampled_arg(cgen, op, arg, dest_reg):
        reg = _pointer(dest_reg)
        #TODO check if reg is valid 32-64 bit pointer
        code, ptr_reg, path = load_struct_ptr(cgen, op)
        if cgen.BIT64:
            code += "lea %s, qword [%s + %s]\n" % (reg, ptr_reg, path)
        else:
            code += "lea %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
        return code, reg, SampledArg

    def _load_sampled_ptr_name_arg(cgen, op, arg, dest_reg):
        reg = _pointer(dest_reg)
        #TODO check if reg is valid 32-64 bit pointer
        if cgen.BIT64:
            code = "mov %s, qword [%s] \n" % (reg, arg.name)
        else:
            code = "mov %s, dword [%s] \n" % (reg, arg.name)

        return code, reg, SampledArgPtr

    def _load_atr_int_arg(cgen, op, arg, dest_reg):
        reg = _general(dest_reg)
        code, ptr_reg, path = load_struct_ptr(cgen, op)
        if cgen.regs.is_reg32(reg):
            code2 = "mov %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
            return code + code2, reg, IntArg

        #Note: if destination is xmm we want implicit conversion to float
        _check_xmm(cgen, reg)
        tmp = cgen.register(typ='general')
        code2 = "mov %s, dword [%s + %s]\n" % (tmp, ptr_reg, path)
        conv = conv_int_to_float(cgen, tmp, reg)
        cgen.release_reg(tmp)
        return code + code2 + conv, reg, FloatArg

    def _load_atr_float_arg(cgen, op, arg, dest_reg):
        xmm = _xmm(dest_reg)
        code, ptr_reg, path = load_struct_ptr(cgen, op)
        if cgen.AVX:
            code2 = "vmovss %s, dword [%s + %s]\n" % (xmm, ptr_reg, path)
        else:
            code2 = "movss %s, dword [%s + %s]\n" % (xmm, ptr_reg, path)
        return code + code2, xmm, FloatArg

    def _load_atr_vec234_arg(cgen, op, arg, dest_reg):
        xmm = _xmm(dest_reg)
        code, ptr_reg, path = load_struct_ptr(cgen, op)
        if cgen.AVX:
            code2 = "vmovaps %s, oword [%s + %s]\n" % (xmm, ptr_reg, path)
        else:
            code2 = "movaps %s, oword [%s + %s]\n" % (xmm, ptr_reg, path)
        return code + code2, xmm, type(arg)

    def _load_atr_rgb_arg(cgen, op, arg, dest_reg):
        xmm = _xmm(dest_reg)
        code, ptr_reg, path = load_struct_ptr(cgen, op)
        if cgen.AVX:
            code2 = "vmovaps %s, oword [%s + %s]\n" % (xmm, ptr_reg, path)
        else:
            code2 = "movaps %s, oword [%s + %s]\n" % (xmm, ptr_reg, path)
        return code + code2, xmm, RGBArg

    def _load_sub_arr_arg(cgen, op, arg, dest_reg):

        #load item from array
        # address = arr_adr + item_size * index
        code, reg, typ = load_operand(cgen, op.index)
        if typ != IntArg:
            raise ValueError("Index in subscript must be Integer!", typ)
        item_size = arg.value.item_size
        code += "imul %s, %s, %i\n" % (reg, reg, item_size)
        if op.path is not None:
            raise ValueError("Todo array argument in structure", op.path)

        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        #TODO check if dest_reg is 32-64 bit pointer
        if cgen.BIT64:
            code += "mov %s, qword [%s] \n" % (dest_reg, arg.name)
            code += "add %s, %s\n" % (dest_reg, 'r' + reg[1:])
        else:
            code += "mov %s, dword [%s] \n" % (dest_reg, arg.name)
            code += "add %s, %s\n" % (dest_reg, reg)
        cgen.release_reg(reg)

        if isinstance(arg.value, ObjArray):
            return code, dest_reg, arg.value.item_arg
        elif isinstance(arg.value, PtrsArray):
            if cgen.BIT64:
                code += "mov %s, qword[%s]\n" % (dest_reg, dest_reg) 
            else:
                code += "mov %s, dword[%s]\n" % (dest_reg, dest_reg) 
            return code, dest_reg, PointerArg
        else:
            raise ValueError("Array not supported yet!", arg.value)

    def _load_sub_vec234_arg(cgen, op, arg, dest_reg):
        # address = arr_adr + item_size * index
        code, reg, typ = load_operand(cgen, op.index)
        if typ != IntArg:
            raise ValueError("Index in subscript must be Integer!", typ)
        xmm = _xmm(dest_reg)
        _check_xmm(cgen, xmm)
        if op.path is not None:
            raise ValueError("Todo!!! array argument in structure", op.path)

        ptr_reg = cgen.register(typ='pointer')
        code += "mov %s, %s\n" % (ptr_reg, arg.name)
        if cgen.BIT64:
            reg = 'r' + reg[1:]
        if cgen.AVX:
            code += "vmovss %s, dword [%s + %s * 4] \n" % (xmm, ptr_reg, reg)
        else:
            code += "movss %s, dword [%s + %s * 4] \n" % (xmm, ptr_reg, reg)

        cgen.release_reg(reg)
        cgen.release_reg(ptr_reg)

        return code, xmm, FloatArg

    def _load_atr_ptr_arg(cgen, op, arg, dest_reg):
        code, ptr_reg, path = load_struct_ptr(cgen, op)
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        #TODO check if dest_reg is pointer
        if cgen.BIT64:
            code2 = "mov %s, qword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        else:
            code2 = "mov %s, dword [%s + %s]\n" % (dest_reg, ptr_reg, path)
        return code + code2, dest_reg, PointerArg

    def _load_name_pointer_arg(cgen, op, arg, dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        #TODO check if dest_reg is pointer
        if cgen.BIT64:
            code = "mov %s, qword [%s]\n" % (dest_reg, arg.name)
        else:
            code = "mov %s, dword [%s]\n" % (dest_reg, arg.name)
        return code, dest_reg, PointerArg

    _ldf = {(Name, IntArg): _load_int_name_arg,
            (Name, FloatArg): _load_float_name_arg,
            (Name, Vec2Arg): _load_vec234_name_arg,
            (Name, Vec3Arg): _load_vec234_name_arg,
            (Name, Vec4Arg): _load_vec234_name_arg,
            (Name, RGBArg): _load_rgb_name_arg,
            (Name, SampledArg): _load_sampled_name_arg,
            (Name, SampledArgPtr): _load_sampled_ptr_name_arg,
            (Const, IntArg): _load_int_name_arg,
            (Const, FloatArg): _load_float_name_arg,
            (Const, Vec2Arg): _load_vec234_name_arg,
            (Const, Vec3Arg): _load_vec234_name_arg,
            (Const, Vec4Arg): _load_vec234_name_arg,
            (Attribute, IntArg): _load_atr_int_arg,
            (Attribute, FloatArg): _load_atr_float_arg,
            (Attribute, Vec2Arg): _load_atr_vec234_arg,
            (Attribute, Vec3Arg): _load_atr_vec234_arg,
            (Attribute, Vec4Arg): _load_atr_vec234_arg,
            (Attribute, RGBArg): _load_atr_rgb_arg,
            (Attribute, SampledArg): _load_atr_sampled_arg,
            (Subscript, ArrayArg): _load_sub_arr_arg,
            (Subscript, RGBArg): _load_sub_vec234_arg,
            (Subscript, Vec2Arg): _load_sub_vec234_arg,
            (Subscript, Vec3Arg): _load_sub_vec234_arg,
            (Subscript, Vec4Arg): _load_sub_vec234_arg,
            (Attribute, PointerArg): _load_atr_ptr_arg,
            (Name, PointerArg): _load_name_pointer_arg
            }

    if isinstance(op, Const):
        arg = cgen.create_const(op)
    else:
        arg = cgen.get_arg(op)
    if arg is None:
        raise ValueError("Argument doesn't exist", op, op.name)
    if isinstance(arg, StructArg):
        arg = arg.resolve(op.path)
    key = (type(op), type(arg))
    if key not in _ldf:
        raise ValueError("Load operand fials! Missing load method.", key)
    code, reg, typ = _ldf[key](cgen, op, arg, dest_reg)
    return code, reg, typ


def arith_cmd(cgen, reg1, typ1, op, reg2, typ2):

    def _ar_pointer_int_arg(cgen, reg1, typ1, op, reg2, typ2):
        ops = {'+': 'add', '-': 'sub'}
        if op not in ops:
            raise ValueError("Only +,- supported for pointer arithmetic.")

        if cgen.BIT64:
            code = '%s %s, %s\n' % (ops[op], reg1, 'r' + reg2[1:])
        else:
            code = '%s %s, %s\n' % (ops[op], reg1, reg2)
        return code, reg1, PointerArg

    def _ar_int_int_arg(cgen, reg1, typ1, op, reg2, typ2):
        ops = {'+': 'add', '-': 'sub', '*': 'imul'}
        #NOTE TODO Implement modulo and division
        code = '%s %s, %s\n' % (ops[op], reg1, reg2)
        return code, reg1, IntArg

    def _ar_float_float_arg(cgen, reg1, typ1, op, reg2, typ2):
        ops_avx = {'+': 'vaddss', '-': 'vsubss', '*': 'vmulss', '/': 'vdivss'}
        ops = {'+': 'addss', '-': 'subss', '*': 'mulss', '/': 'divss'}
        if cgen.AVX:
            code = "%s %s, %s, %s \n" % (ops_avx[op], reg1, reg1, reg2)
        else:
            code = "%s %s, %s \n" % (ops[op], reg1, reg2)
        return code, reg1, FloatArg

    def _ar_int_float_arg(cgen, reg1, typ1, op, reg2, typ2):
        ops_avx = {'+': 'vaddss', '-': 'vsubss', '*': 'vmulss', '/': 'vdivss'}
        ops = {'+': 'addss', '-': 'subss', '*': 'mulss', '/': 'divss'}
        tmp = cgen.register(typ='xmm')
        code = conv_int_to_float(cgen, reg1, tmp)
        if cgen.AVX:
            code2 = "%s %s, %s, %s \n" % (ops_avx[op], tmp, tmp, reg2)
        else:
            code2 = "%s %s, %s \n" % (ops[op], tmp, reg2)
        return code + code2, tmp, FloatArg

    def _ar_float_int_arg(cgen, reg1, typ1, op, reg2, typ2):
        ops_avx = {'+': 'vaddss', '-': 'vsubss', '*': 'vmulss', '/': 'vdivss'}
        ops = {'+': 'addss', '-': 'subss', '*': 'mulss', '/': 'divss'}
        tmp = cgen.register(typ='xmm')
        code = conv_int_to_float(cgen, reg2, tmp)
        if cgen.AVX:
            code2 = "%s %s, %s, %s \n" % (ops_avx[op], reg1, reg1, tmp)
        else:
            code2 = "%s %s, %s \n" % (ops[op], reg1, tmp)
        cgen.release_reg(tmp)
        return code + code2, reg1, FloatArg

    def _ar_v234_v234_arg(cgen, reg1, typ1, op, reg2, typ2):
        ops_avx = {'+': 'vaddps', '-': 'vsubps', '*': 'vmulps', '/': 'vdivps'}
        ops = {'+': 'addps', '-': 'subps', '*': 'mulps', '/': 'divps'}
        if cgen.AVX:
            code = "%s %s, %s, %s \n" % (ops_avx[op], reg1, reg1, reg2)
        else:
            code = "%s %s, %s \n" % (ops[op], reg1, reg2)
        return code, reg1, typ1

    def _ar_v234_int_arg(cgen, reg1, typ1, op, reg2, typ2):
        if op != '*':
            raise ValueError("Only multiplication is allowed.", typ1, typ2)
        tmp = cgen.register(typ='xmm')
        code = conv_int_to_float(cgen, reg2, tmp)
        if cgen.AVX:  # vblends maybe is faster investigate TODO
            code2 = "vshufps %s, %s, %s, 0x00\n" % (tmp, tmp, tmp)
            code3 = "vmulps %s, %s, %s \n" % (reg1, reg1, tmp)
        else:
            code2 = "shufps %s, %s, 0x00\n" % (tmp, tmp)
            code3 = "mulps %s, %s \n" % (reg1, tmp)
        cgen.release_reg(tmp)
        return code + code2 + code3, reg1, typ1

    def _ar_int_v234_arg(cgen, reg1, typ1, op, reg2, typ2):
        if op != '*':
            raise ValueError("Only multiplication is allowed.", typ1, typ2)
        tmp = cgen.register(typ='xmm')
        code = conv_int_to_float(cgen, reg1, tmp)
        if cgen.AVX:  # vblends maybe is faster investigate TODO
            code2 = "vshufps %s, %s, %s, 0x00\n" % (tmp, tmp, tmp)
            code3 = "vmulps %s, %s, %s \n" % (tmp, tmp, reg2)
        else:
            code2 = "shufps %s, %s, 0x00\n" % (tmp, tmp)
            code3 = "mulps %s, %s \n" % (tmp, reg2)
        return code + code2 + code3, tmp, typ2

    def _ar_float_v234_arg(cgen, reg1, typ1, op, reg2, typ2):
        if op != '*':
            raise ValueError("Only multiplication is allowed.", typ1, typ2)
        if cgen.AVX:  # vblends maybe is faster investigate TODO
            code = "vshufps %s, %s, %s, 0x00\n" % (reg1, reg1, reg1)
            code2 = "vmulps %s, %s, %s \n" % (reg1, reg1, reg2)
        else:
            code = "shufps %s, %s, 0x00\n" % (reg1, reg1)
            code2 = "mulps %s, %s \n" % (reg1, reg2)
        return code + code2, reg1, typ2

    def _ar_v234_float_arg(cgen, reg1, typ1, op, reg2, typ2):
        if op != '*':
            raise ValueError("Only multiplication is allowed.", typ1, typ2)
        if cgen.AVX:  # vblends maybe is faster investigate TODO
            code = "vshufps %s, %s, %s, 0x00\n" % (reg2, reg2, reg2)
            code2 = "vmulps %s, %s, %s \n" % (reg1, reg1, reg2)
        else:
            code = "shufps %s, %s, 0x00\n" % (reg2, reg2)
            code2 = "mulps %s, %s \n" % (reg1, reg2)
        return code + code2, reg1, typ1

    def _ar_sampled_sampled_arg(cgen, reg1, typ1, op, reg2, typ2):
        used_xmms = cgen.get_used_xmms()
        prolog = cgen.save_regs(used_xmms)

        sam_arg = cgen.create_tmp_spec()
        if not isinstance(sam_arg, SampledArg):
            raise ValueError("Sampled argument is expected", sam_arg)

        dst_reg = cgen.register(typ='pointer')
        ld_sam = 'mov %s, %s\n' % (dst_reg, sam_arg.name)

        n = len(sam_arg.value.samples)
        ar = arithmetic_sampled(cgen, reg1, op, reg2, dst_reg, n)

        epilog = cgen.load_regs(used_xmms)
        code = prolog + ld_sam + ar + epilog
        return code, dst_reg, SampledArg

    def _expand_to_xmm7(cgen, xmm, typ):
        def _conv_int_to_float(cgen, reg, xmm):
            if cgen.AVX:
                return "vcvtsi2ss %s, %s, %s \n" % (xmm, xmm, reg)
            else:
                return "cvtsi2ss %s, %s \n" % (xmm, reg)
        expand = ''
        if typ is IntArg:
            expand = _conv_int_to_float(cgen, xmm, 'xmm7')
            xmm = 'xmm7'

        if cgen.AVX:
            expand += "vshufps %s, %s, %s, 0x00\n" % (xmm, xmm, xmm)
            xmm = "y" + xmm[1:]
            expand += "vperm2f128 %s, %s, %s, 0x00 \n" % (xmm, xmm, xmm)
            if xmm != 'ymm7':
                expand += "vmovaps %s, %s\n" % ('ymm7', xmm)
        else:
            expand += "shufps %s, %s, 0x00\n" % (xmm, xmm)
            if xmm != 'xmm7':
                expand += "movaps %s, %s\n" % ('xmm7', xmm)
        return expand

    def _ar_sampled_float_arg(cgen, reg1, typ1, op, xmm, typ2):
        if op != '*':
            raise ValueError("Only multiplication is allowed", typ1, typ2)

        used_xmms = cgen.get_used_xmms()
        prolog = cgen.save_regs(used_xmms)

        sam_arg = cgen.create_tmp_spec()
        dst_reg = cgen.register(typ='pointer')
        ld_sam = 'mov %s, %s\n' % (dst_reg, sam_arg.name)

        expand = _expand_to_xmm7(cgen, xmm, typ2)

        n = len(sam_arg.value.samples)
        ar = arith_sampled_mult(cgen, reg1, dst_reg, n)

        epilog = cgen.load_regs(used_xmms)
        code = prolog + ld_sam + expand + ar + epilog
        return code, dst_reg, SampledArg

    def _ar_float_sampled_arg(cgen, xmm, typ1, op, reg2, typ2):
        if op != '*':
            raise ValueError("Only multiplication is allowed", typ1, typ2)

        used_xmms = cgen.get_used_xmms()
        prolog = cgen.save_regs(used_xmms)

        sam_arg = cgen.create_tmp_spec()
        dst_reg = cgen.register(typ='pointer')
        ld_sam = 'mov %s, %s\n' % (dst_reg, sam_arg.name)

        expand = _expand_to_xmm7(cgen, xmm, typ1)

        n = len(sam_arg.value.samples)
        ar = arith_sampled_mult(cgen, reg2, dst_reg, n)

        epilog = cgen.load_regs(used_xmms)
        code = prolog + ld_sam + expand + ar + epilog
        return code, dst_reg, SampledArg


    _arf = {(IntArg, IntArg): _ar_int_int_arg,
            (FloatArg, FloatArg): _ar_float_float_arg,
            (IntArg, FloatArg): _ar_int_float_arg,
            (FloatArg, IntArg): _ar_float_int_arg,
            (Vec2Arg, Vec2Arg): _ar_v234_v234_arg,
            (Vec3Arg, Vec3Arg): _ar_v234_v234_arg,
            (Vec4Arg, Vec4Arg): _ar_v234_v234_arg,
            (Vec2Arg, IntArg): _ar_v234_int_arg,
            (Vec3Arg, IntArg): _ar_v234_int_arg,
            (Vec3Arg, IntArg): _ar_v234_int_arg,
            (IntArg, Vec2Arg): _ar_int_v234_arg,
            (IntArg, Vec3Arg): _ar_int_v234_arg,
            (IntArg, Vec4Arg): _ar_int_v234_arg,
            (Vec2Arg, FloatArg): _ar_v234_float_arg,
            (Vec3Arg, FloatArg): _ar_v234_float_arg,
            (Vec4Arg, FloatArg): _ar_v234_float_arg,
            (FloatArg, Vec2Arg): _ar_float_v234_arg,
            (FloatArg, Vec3Arg): _ar_float_v234_arg,
            (FloatArg, Vec4Arg): _ar_float_v234_arg,
            (RGBArg, RGBArg): _ar_v234_v234_arg,
            (RGBArg, IntArg): _ar_v234_int_arg,
            (RGBArg, FloatArg): _ar_v234_float_arg,
            (IntArg, RGBArg): _ar_int_v234_arg,
            (FloatArg, RGBArg): _ar_float_v234_arg,
            (PointerArg, IntArg): _ar_pointer_int_arg,
            (SampledArg, SampledArg): _ar_sampled_sampled_arg,
            (SampledArg, FloatArg): _ar_sampled_float_arg,
            (SampledArg, IntArg): _ar_sampled_float_arg,
            (FloatArg, SampledArg): _ar_float_sampled_arg,
            (IntArg, SampledArg): _ar_float_sampled_arg,
            (SampledArg, SampledArgPtr): _ar_sampled_sampled_arg,
            (SampledArgPtr, SampledArg): _ar_sampled_sampled_arg,
            }

    key = (typ1, typ2)
    if key not in _arf:
        raise ValueError("Arithmetic is not defined!", key, reg1, typ1, op, reg2, typ2)
    code, reg, typ = _arf[key](cgen, reg1, typ1, op, reg2, typ2)
    return code, reg, typ


def process_operand(cgen, op, regs=None):
    if isinstance(op, Callable):
        regs = [] if regs is None else regs
        return cgen.generate_callable(op, regs)
    code, reg, typ = load_operand(cgen, op)
    return (code, reg, typ)


def process_operation(cgen, operation, stack=[]):

    left = operation.left
    right = operation.right
    op = operation.operator
    regs = [reg for reg, typ in stack]
    if not left is NoOp and not right is NoOp:
        code, reg, typ = process_operand(cgen, left, regs=regs)
        regs.append(reg)
        code2, reg2, typ2 = process_operand(cgen, right, regs=regs)
        code += code2
    elif left is NoOp and right is NoOp:
        reg2, typ2 = stack.pop()
        reg, typ = stack.pop()
        code = ''
    elif left is NoOp and not right is NoOp:
        reg, typ = stack.pop()
        code, reg2, typ2 = process_operand(cgen, right, regs=regs)
    elif not left is NoOp and right is NoOp:
        code, reg, typ = process_operand(cgen, left, regs=regs)
        reg2, typ2 = stack.pop()
    else:
        raise ValueError("Operation is wrong!", left, right, operation)

    code3, reg3, typ3 = arith_cmd(cgen, reg, typ, op, reg2, typ2)

    if reg3 != reg:
        cgen.release_reg(reg)
    if reg3 != reg2:
        cgen.release_reg(reg2)

    stack.append((reg3, typ3))
    return code + code3, reg3, typ3


def process_expression(cgen, expr):
    if not isinstance(expr, Operations):
        code, reg, typ = process_operand(cgen, expr)
        return code, reg, typ
    stack = []
    code = ''
    for operation in expr.operations:
        co, reg, typ = process_operation(cgen, operation, stack)
        code += co
    return code, reg, typ


def move_reg_to_reg(cgen, src_reg, dst_reg):
    if src_reg == dst_reg:
        return ''
    if cgen.regs.is_reg32(src_reg) and cgen.regs.is_reg32(dst_reg):
        code = "mov %s, %s\n" % (dst_reg, src_reg)
    elif cgen.regs.is_reg64(src_reg) and cgen.regs.is_reg64(dst_reg):
        code = "mov %s, %s\n" % (dst_reg, src_reg)
    elif cgen.regs.is_xmm(src_reg) and cgen.regs.is_xmm(dst_reg):
        if cgen.AVX:
            code = "vmovaps %s, %s\n" % (dst_reg, src_reg)
        else:
            code = "movaps %s, %s\n" % (dst_reg, src_reg)
    else:
        raise ValueError("Unsuported combination of regs!", src_reg, dst_reg)
    return code


def move_reg_to_mem(cgen, reg, name):
    if cgen.regs.is_reg32(reg):
        code = "mov dword [%s], %s\n" % (name, reg)
    elif cgen.regs.is_reg64(reg):
        code = "mov qword [%s], %s\n" % (name, reg)
    elif cgen.regs.is_xmm(reg):
        if cgen.AVX:
            code = "vmovaps oword [%s], %s\n" % (name, reg)
        else:
            code = "movaps oword [%s], %s\n" % (name, reg)
    else:
        raise ValueError("Unsuported register!", reg)
    return code


def move_mem_to_reg(cgen, reg, name):
    if cgen.regs.is_reg32(reg):
        code = "mov %s, dword [%s]\n" % (reg, name)
    elif cgen.regs.is_reg64(reg):
        code = "mov %s, qword [%s]\n" % (reg, name)
    elif cgen.regs.is_xmm(reg):
        if cgen.AVX:
            code = "vmovaps %s, oword [%s]\n" % (reg, name)
        else:
            code = "movaps %s, oword [%s]\n" % (reg, name)
    else:
        raise ValueError("Unsuported register!", reg)
    return code


def move_reg_to_acum(cgen, reg, typ):
    acum = cgen.acum_for_type(typ)
    return move_reg_to_reg(cgen, reg, acum)


def zero_register(cgen, reg):
    if cgen.regs.is_reg32(reg):
        code = "xor %s, %s\n" % (reg, reg)
    elif cgen.regs.is_reg64(reg):
        code = "xor %s, %s\n" % (reg, reg)
    elif cgen.regs.is_xmm(reg):
        if cgen.AVX:
            code = "vpxor %s, %s, %s\n" % (reg, reg, reg)
        else:
            code = "pxor %s, %s\n" % (reg, reg)
    else:
        raise ValueError("Unsuported register!", reg)
    return code


def compare_ints(cgen, reg1, con, reg2, label):
    #if condition is met not jump to end of if
    code = "cmp %s, %s\n" % (reg1, reg2)
    cons = {'==': 'jne', '<': 'jge', '>': 'jle',
            '<=': 'jg', '>=': 'jl', '!=': 'je'}
    code += "%s %s\n" % (cons[con], label)
    return code


def compare_floats(cgen, xmm1, con, xmm2, label):
    if cgen.AVX:
        code = "vcomiss %s, %s\n" % (xmm1, xmm2)
    else:
        code = "comiss %s, %s\n" % (xmm1, xmm2)
    cons = {'==': 'jnz', '<': 'jnc', '>': 'jc', '!=': 'jz'}
    code += "%s %s\n" % (cons[con], label)
    return code


def generate_test(cgen, test, end_label):
    if len(test.conditions) != 1:
        raise ValueError("Only one condtion for now!", test.conditions)
    condition = test.conditions[0]
    code1, reg1, typ1 = load_operand(cgen, condition.left)
    if condition.right is NoOp:
        if typ1 != IntArg:
            raise ValueError("Only int for single argument condition.")
        line1 = "cmp %s, 0\n" % reg1
        line2 = "je %s\n" % end_label
        code = code1 + line1 + line2
        return code

    code2, reg2, typ2 = load_operand(cgen, condition.right)
    code = code1 + code2
    if typ1 == IntArg and typ2 == IntArg:
        code += compare_ints(cgen, reg1, condition.operator, reg2, end_label)
    elif typ1 == FloatArg and typ2 == FloatArg:
        code += compare_floats(cgen, reg1, condition.operator, reg2, end_label)
    elif typ1 == IntArg and typ2 == FloatArg:
        xmm = cgen.register(typ='xmm')
        code += conv_int_to_float(cgen, reg1, xmm)
        code += compare_floats(cgen, xmm, condition.operator, reg2, end_label)
    elif typ1 == FloatArg and typ2 == IntArg:
        xmm = cgen.register(typ='xmm')
        code += conv_int_to_float(cgen, reg2, xmm)
        code += compare_floats(cgen, reg1, condition.operator, xmm, end_label)
    else:
        raise ValueError("Unsuported operands types", typ1, typ2)
    return code


def store_func_args(cgen, args):
    xmms = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    for arg in args:
        if isinstance(arg, StructArgPtr):
            reg = general.pop()
            if cgen.BIT64:
                code += "mov qword [%s], %s\n" % (arg.name, 'r' + reg[1:])
            else:
                code += "mov dword [%s], %s\n" % (arg.name, reg)
        elif isinstance(arg, IntArg):
            reg = general.pop()
            code += "mov dword [%s], %s\n" % (arg.name, reg)
        elif isinstance(arg, FloatArg):
            xmm = xmms.pop()
            if cgen.AVX:
                code += "vmovss dword [%s], %s \n" % (arg.name, xmm)
            else:
                code += "movss dword [%s], %s \n" % (arg.name, xmm)
        elif isinstance(arg, (Vec2Arg, Vec3Arg, Vec4Arg, RGBArg)):
            xmm = xmms.pop()
            if cgen.AVX:
                code += "vmovaps oword [%s], %s \n" % (arg.name, xmm)
            else:
                code += "movaps oword [%s], %s \n" % (arg.name, xmm)
        elif isinstance(arg, SampledArgPtr):
            reg = general.pop()
            if cgen.BIT64:
                code += "mov qword [%s], %s\n" % (arg.name, 'r' + reg[1:])
            else:
                code += "mov dword [%s], %s\n" % (arg.name, reg)
        else:
            raise ValueError("Currently unsuported argument.", arg)
    return code


def load_func_args(cgen, operands, args):
    if len(operands) != len(args):
        raise ValueError("Argument length mismatch", operands, args)

    def _load_struct_ptr(cgen, operand, ptr_reg):
        str_arg = cgen.get_arg(operand)
        if isinstance(str_arg, StructArgPtr):
            if cgen.BIT64:
                code = "mov %s, qword [%s] \n" % (ptr_reg, str_arg.name)
            else:
                code = "mov %s, dword [%s] \n" % (ptr_reg, str_arg.name)
        else:
            code = "mov %s, %s \n" % (ptr_reg, str_arg.name)
        path = "%s.%s" % (str_arg.type_name, operand.path)
        return code, path

    def _load_int_int_arg(cgen, operand, arg, xmms, regs, ptr_reg):
        reg = regs.pop()
        if isinstance(operand, (Name, Const)):
            code = "mov %s, dword [%s] \n" % (reg, arg.name)
        elif isinstance(operand, Attribute):
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            code += "mov %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
        else:
            raise ValueError("Could not load argument", operand)
        return code

    def _load_float_float_arg(cgen, operand, arg, xmms, regs, ptr_reg):
        xmm = xmms.pop()
        if isinstance(operand, (Name, Const)):
            if cgen.AVX:
                code = "vmovss %s, dword [%s] \n" % (xmm, arg.name)
            else:
                code = "movss %s, dword [%s] \n" % (xmm, arg.name)
        elif isinstance(operand, Attribute):
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            if cgen.AVX:
                code += "vmovss %s, dword [%s + %s]\n" % (xmm, ptr_reg, path)
            else:
                code += "movss %s, dword [%s + %s]\n" % (xmm, ptr_reg, path)
        else:
            raise ValueError("Could not load argument", operand)
        return code

    def _load_float_int_arg(cgen, operand, arg, xmms, regs, ptr_reg):
        xmm = xmms.pop()
        reg = regs[0]
        if isinstance(operand, (Name, Const)):
            code = "mov %s, dword [%s] \n" % (reg, arg.name)
        elif isinstance(operand, Attribute):
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            code += "mov %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
        else:
            raise ValueError("Could not load argument", operand)
        code += conv_int_to_float(cgen, reg, xmm)
        return code

    def _load_vec234_vec234_arg(cgen, operand, arg, xmms, regs, ptr_reg):
        xmm = xmms.pop()
        if isinstance(operand, (Name, Const)):
            if cgen.AVX:
                code = "vmovaps %s, oword [%s] \n" % (xmm, arg.name)
            else:
                code = "movaps %s, oword [%s] \n" % (xmm, arg.name)
        elif isinstance(operand, Attribute):
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            if cgen.AVX:
                code += "vmovaps %s, oword [%s + %s]\n" % (xmm, ptr_reg, path)
            else:
                code += "movaps %s, oword [%s + %s]\n" % (xmm, ptr_reg, path)
        else:
            raise ValueError("Could not load argument", operand)
        return code

    def _load_struct_arg_ptr(cgen, operand, arg, xmms, regs, ptr_reg):
        reg = regs.pop()
        if isinstance(operand, Name):
            reg = 'r' + reg[1:] if cgen.BIT64 else reg
            code = "mov %s, %s\n" % (reg, arg.name)
        elif isinstance(operand, Attribute):
            raise ValueError("Test this! TODO: lea or mov??", operand)
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            if cgen.BIT64:
                reg = 'r' + reg[1:]
                code += "mov %s, qword [%s + %s]\n" % (reg, ptr_reg, path)
            else:
                code += "mov %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
        else:
            raise ValueError("Could not load argument!", operand)
        return code

    def _load_struct_arg_ptr_ptr(cgen, operand, arg, xmms, regs, ptr_reg):
        reg = regs.pop()
        if isinstance(operand, Name):
            if cgen.BIT64:
                code = "mov %s, qword [%s] \n" % ('r' + reg[1:], arg.name)
            else:
                code = "mov %s, dword [%s] \n" % (reg, arg.name)
        elif isinstance(operand, Attribute):  # TODO
            raise ValueError("This is not tested!!!", operand.name, operand.path)
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            reg = 'r' + reg[1:] if cgen.BIT64 else reg
            if cgen.BIT64:
                code += "lea %s, qword [%s + %s]\n" % (reg, ptr_reg, path)
            else:
                code += "lea %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
        else:
            raise ValueError("Could not load argument!", operand)
        return code

    def _load_sam_ptr_sam(cgen, operand, arg, xmms, regs, ptr_reg):
        reg = regs.pop()
        reg = 'r' + reg[1:] if cgen.BIT64 else reg
        if isinstance(operand, Name):
            code = 'mov %s, %s\n' % (reg, arg.name)
        elif isinstance(operand, Attribute):
            code, path = _load_struct_ptr(cgen, operand, ptr_reg)
            reg = 'r' + reg[1:] if cgen.BIT64 else reg
            if cgen.BIT64:
                code += "lea %s, qword [%s + %s]\n" % (reg, ptr_reg, path)
            else:
                code += "lea %s, dword [%s + %s]\n" % (reg, ptr_reg, path)
        else:
            raise ValueError("Could not load argument!", operand)
        return code

    xmms = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    regs = ['edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    ptr_reg = 'rbp' if cgen.BIT64 else 'ebp'

    _ldf = {(IntArg, IntArg): _load_int_int_arg,
            (FloatArg, FloatArg): _load_float_float_arg,
            (FloatArg, IntArg): _load_float_int_arg,
            (Vec2Arg, Vec2Arg): _load_vec234_vec234_arg,
            (Vec3Arg, Vec3Arg): _load_vec234_vec234_arg,
            (Vec4Arg, Vec4Arg): _load_vec234_vec234_arg,
            (RGBArg, RGBArg): _load_vec234_vec234_arg,
            (StructArgPtr, StructArg): _load_struct_arg_ptr,
            (StructArgPtr, StructArgPtr): _load_struct_arg_ptr_ptr,
            (SampledArgPtr, SampledArg): _load_sam_ptr_sam,
            }

    code = ''
    for operand, arg in zip(operands, args):
        if isinstance(operand, Const):
            arg2 = cgen.create_const(operand)
        else:
            arg2 = cgen.get_arg(operand)
        if isinstance(arg2, StructArg):
            if isinstance(operand, Attribute):
                arg2 = arg2.resolve(operand.path)
        if isinstance(arg, StructArgPtr) and isinstance(arg2, StructArg):
            if arg.type_name != arg2.type_name:
                raise ValueError("Different type of structures!", arg, arg2)

        key = (type(arg), type(arg2))
        if key not in _ldf:
            raise ValueError("Could not load function arg", arg, arg2, operand, operand.name)
        code += _ldf[key](cgen, operand, arg2, xmms, regs, ptr_reg)
    return code


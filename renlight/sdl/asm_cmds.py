
from .utils import float2hex
from .strs import Attribute, Name, Callable, Const, Subscript, Operations
from .args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg


def conv_int_to_float(cgen, reg, xmm):
    if not cgen.regs.is_xmm(xmm):
        raise ValueError("xmm register is expected not %s" % xmm)
    if not cgen.regs.is_reg32(xmm):
        raise ValueError("reg32 register is expected not %s" % reg)
    if cgen.AVX:
        return "vcvtsi2ss %s, %s, %s \n" % (xmm, xmm, reg)
    else:
        return "cvtsi2ss %s, %s \n" % (xmm, reg)


def conv_float_to_int(cgen, reg, xmm):
    if not cgen.regs.is_xmm(xmm):
        raise ValueError("xmm register is expected not %s" % xmm)
    if not cgen.regs.is_reg32(xmm):
        raise ValueError("reg32 register is expected not %s" % reg)
    if cgen.AVX:
        return "vcvttss2si %s, %s \n" % (reg, xmm)
    else:
        return "cvttss2si %s, %s \n" % (reg, xmm)


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

    _stf = {(Name, IntArg): _store_int_name_const,
            (Name, FloatArg): _store_float_name_const,
            (Name, Vec2Arg): _store_vec2_name_const,
            (Name, Vec3Arg): _store_vec2_name_const,
            (Name, Vec4Arg): _store_vec2_name_const
            }

    arg = cgen.create_arg(dest, const)
    if isinstance(dest, (Name, Attribute, Subscript)):
        key = (type(dest), type(arg))
        if key not in _stf:
            raise ValueError("Store const fials! Missing store method.", key)
        code = _stf[key](cgen, dest, const.const, arg)
        return code
    raise ValueError("Store const, unsuported destination!", dest)


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

    _stf = {(Name, IntArg): _store_int_name_arg,
            (Name, FloatArg): _store_float_name_arg,
            (Name, Vec2Arg): _store_vec234_name_arg,
            (Name, Vec3Arg): _store_vec234_name_arg,
            (Name, Vec4Arg): _store_vec234_name_arg
            }

    arg = cgen.create_arg(dest, typ)
    key = (type(dest), type(arg))
    if key not in _stf:
        raise ValueError("Store operand fials! Missing store method.", key)
    code = _stf[key](cgen, dest, reg, arg)
    return code


def load_operand(cgen, op, dest_reg=None, ptr_reg=None):

    def _general(dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='general')
        return dest_reg

    def _xmm(dest_reg):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
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

    _ldf = {(Name, IntArg): _load_int_name_arg,
            (Name, FloatArg): _load_float_name_arg,
            (Name, Vec2Arg): _load_vec234_name_arg,
            (Name, Vec3Arg): _load_vec234_name_arg,
            (Name, Vec4Arg): _load_vec234_name_arg
            }

    arg = cgen.get_arg(op)
    if arg is None:
        raise ValueError("Argument doesn't exist", op, op.name)
    key = (type(op), type(arg))
    if key not in _ldf:
        raise ValueError("Load operand fials! Missing load method.", key)
    code, reg, typ = _ldf[key](cgen, op, arg, dest_reg)
    return code, reg, typ


def process_operand(cgen, op):
    if isinstance(op, Callable):
        raise ValueError("Callable not yet implemented")
    code, reg, typ = load_operand(cgen, op)
    return (code, reg, typ)


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


def move_reg_to_acum(cgen, reg, typ):
    raise NotImplementedError()


def generate_test(cgen, test, end_label):
    raise NotImplementedError()

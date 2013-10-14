
from .utils import float2hex
from .strs import Attribute, Name, Callable, Const, Subscript, Operations, NoOp
from .args import IntArg, FloatArg, Vec2Arg, Vec3Arg,\
    Vec4Arg, StructArg, StructArgPtr
from .arr import ArrayArg


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

    def _store_name_struct_arg(cgen, dest, reg, arg):
        if cgen.BIT64:
            return "mov qword [%s], %s \n" % (arg.name, reg)
        else:
            return "mov dword [%s], %s \n" % (arg.name, reg)

    _stf = {(Name, IntArg): _store_int_name_arg,
            (Name, FloatArg): _store_float_name_arg,
            (Name, Vec2Arg): _store_vec234_name_arg,
            (Name, Vec3Arg): _store_vec234_name_arg,
            (Name, Vec4Arg): _store_vec234_name_arg,
            (Attribute, IntArg): _store_atr_int_arg,
            (Attribute, FloatArg): _store_atr_flt_arg,
            (Attribute, Vec2Arg): _store_atr_vec234_arg,
            (Attribute, Vec3Arg): _store_atr_vec234_arg,
            (Attribute, Vec4Arg): _store_atr_vec234_arg,
            (Name, StructArgPtr): _store_name_struct_arg
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

        if not isinstance(arg.value.item_arg, StructArg):
            raise ValueError("Only struct array are supported!!", op.path)

        if dest_reg is None:
            dest_reg = cgen.register(typ='pointer')
        #TODO check if dest_reg is pointer
        if cgen.BIT64:
            code += "mov %s, qword [%s] \n" % (dest_reg, arg.name)
            code += "add %s, %s\n" % (dest_reg, 'r' + reg[1:])
        else:
            code += "mov %s, dword [%s] \n" % (dest_reg, arg.name)
            code += "add %s, %s\n" % (dest_reg, reg)

        cgen.release_reg(reg)
        return code, dest_reg, arg.value.item_arg

    _ldf = {(Name, IntArg): _load_int_name_arg,
            (Name, FloatArg): _load_float_name_arg,
            (Name, Vec2Arg): _load_vec234_name_arg,
            (Name, Vec3Arg): _load_vec234_name_arg,
            (Name, Vec4Arg): _load_vec234_name_arg,
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
            (Subscript, ArrayArg): _load_sub_arr_arg
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
            (Vec3Arg, FloatArg): _ar_v234_float_arg,
            (FloatArg, Vec2Arg): _ar_float_v234_arg,
            (FloatArg, Vec3Arg): _ar_float_v234_arg,
            (FloatArg, Vec4Arg): _ar_float_v234_arg,
            }

    key = (typ1, typ2)
    if key not in _arf:
        raise ValueError("Arithmetic is nod defined!", key)
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

    #xmms = []
    #NOTE We save xmm registers because SampledSpec
    # uses all xmm registers for arithmetic
    # if typ is SampledSpec or typ2 is SampledSpec:
    #     xmms = [r for r, t in stack if cgen.is_xmm(r)]
    #sregs = cgen.save_regs(xmms)
    code3, reg3, typ3 = arith_cmd(cgen, reg, typ, op, reg2, typ2)
    #lregs = cgen.load_regs(xmms)

    if reg3 != reg:
        cgen.release_reg(reg)
    if reg3 != reg2:
        cgen.release_reg(reg2)

    stack.append((reg3, typ3))
    #return code + sregs + code3 + lregs, reg3, typ3
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
        elif isinstance(arg, (Vec2Arg, Vec3Arg, Vec4Arg)):
            xmm = xmms.pop()
            if cgen.AVX:
                code += "vmovaps oword [%s], %s \n" % (arg.name, xmm)
            else:
                code += "movaps oword [%s], %s \n" % (arg.name, xmm)
        else:
            raise ValueError("Currently unsuported argument.", arg)
    return code


def load_func_args(cgen, operands, args):
    if len(operands) != len(args):
        raise ValueError("Argument length mismatch", operands, args)

    def _load_struct_ptr(cgen, operand, ptr_reg):
        str_arg = cgen.get_arg(operand)
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
            raise ValueError("Not load argument Implement this.", operand)
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
            (StructArgPtr, StructArg): _load_struct_arg_ptr,
            (StructArgPtr, StructArgPtr): _load_struct_arg_ptr_ptr,
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
            raise ValueError("Could not load function arg", arg, arg2, operand)
        code += _ldf[key](cgen, operand, arg2, xmms, regs, ptr_reg)
    return code


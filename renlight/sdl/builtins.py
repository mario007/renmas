
from .args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg
from .asm_cmds import load_operand, conv_float_to_int, conv_int_to_float,\
    zero_register
from .cgen import register_function


def _int_function(cgen, operands):
    if len(operands) == 0:
        reg = cgen.register(typ='general')
        code = "xor %s, %s\n" % (reg, reg)
        return code, reg, IntArg

    if len(operands) != 1:
        raise ValueError("Wrong number of arguments in int function", operands)
    code, reg, typ = load_operand(cgen, operands[0])
    if typ != IntArg and typ != FloatArg:
        raise ValueError("Unsuported argument type", operands[0], typ)

    if typ == IntArg:
        return code, reg, typ

    to_reg = cgen.register(typ="general")
    code += conv_float_to_int(cgen, to_reg, reg)
    cgen.release_reg(reg)
    return code, to_reg, IntArg

register_function('int', _int_function, inline=True)


def _float_function(cgen, operands):
    if len(operands) == 0:
        xmm = cgen.register(typ='xmm')
        if cgen.AVX:
            code = "vpxor %s, %s, %s\n" % (xmm, xmm, xmm)
        else:
            code = "pxor %s, %s\n" % (xmm, xmm)
        return code, xmm, FloatArg

    if len(operands) != 1:
        raise ValueError("Wrong number of arguments float function", operands)

    code, reg, typ = load_operand(cgen, operands[0])
    if typ != IntArg and typ != FloatArg:
        raise ValueError("Unsuported argument type", operands[0], typ)

    if typ == FloatArg:
        return code, reg, typ

    xmm = cgen.register(typ='xmm')
    code += conv_int_to_float(cgen, reg, xmm)
    cgen.release_reg(reg)
    return code, xmm, FloatArg

register_function('float', _float_function, inline=True)


def _combine_two_floats(cgen, op1, op2):
    xmm1 = cgen.register(typ='xmm')
    xmm2 = cgen.register(typ='xmm')
    code = zero_register(cgen, xmm1)
    code += zero_register(cgen, xmm2)
    code1, reg1, typ1 = load_operand(cgen, op1, dest_reg=xmm1)
    code2, reg2, typ2 = load_operand(cgen, op2, dest_reg=xmm2)
    code += code1 + code2

    if typ1 != FloatArg or typ2 != FloatArg:
        raise ValueError("Only floats are allowed!", typ1, typ2)

    if cgen.AVX:
        code += "vpslldq %s, %s, 4\n" % (xmm2, xmm2)
        code += "vorps %s, %s, %s\n" % (xmm1, xmm1, xmm2)
    else:
        code += "pslldq %s, 4\n" % xmm2
        code += "orps %s, %s\n" % (xmm1, xmm2)
    cgen.release_reg(xmm2)
    return code, xmm1


def _add_float(cgen, xmm, op, offset):
    xmm2 = cgen.register(typ='xmm')
    code = zero_register(cgen, xmm2)
    code1, reg1, typ1 = load_operand(cgen, op, dest_reg=xmm2)
    code += code1

    if typ1 != FloatArg:
        raise ValueError("Argument must be floats!", typ1)
    if cgen.AVX:
        code += "vpslldq %s, %s, %i\n" % (xmm2, xmm2, offset)
        code += "vorps %s, %s, %s\n" % (xmm, xmm, xmm2)
    else:
        code += "pslldq %s, %i\n" % (xmm2, offset)
        code += "orps %s, %s\n" % (xmm, xmm2)

    cgen.release_reg(xmm2)
    return code, xmm


def _float2_function(cgen, operands):
    if len(operands) != 2:
        raise ValueError("Wrong number of operands in float2 func.", operands)

    code, xmm = _combine_two_floats(cgen, operands[0], operands[1])
    return code, xmm, Vec2Arg

register_function('float2', _float2_function, inline=True)


def _float3_function(cgen, operands):
    if len(operands) != 3:
        raise ValueError("Wrong number of operands in float3 func.", operands)

    code1, xmm = _combine_two_floats(cgen, operands[0], operands[1])
    code2, xmm = _add_float(cgen, xmm, operands[2], 8)
    return code1 + code2, xmm, Vec3Arg

register_function('float3', _float3_function, inline=True)


def _float4_function(cgen, operands):
    if len(operands) != 4:
        raise ValueError("Wrong number of operands in float3 func.", operands)

    code1, xmm = _combine_two_floats(cgen, operands[0], operands[1])
    code2, xmm = _add_float(cgen, xmm, operands[2], 8)
    code3, xmm = _add_float(cgen, xmm, operands[3], 12)
    return code1 + code2 + code3, xmm, Vec4Arg

register_function('float4', _float4_function, inline=True)


def _dot_function(cgen, operands):
    if len(operands) != 2:
        raise ValueError("Wrong number of operands in dot fucntion", operands)
    code1, reg1, typ1 = load_operand(cgen, operands[0])
    code2, reg2, typ2 = load_operand(cgen, operands[1])

    if typ1 != Vec3Arg or typ2 != Vec3Arg:
        raise ValueError("dot function expect two Vec3Arg.", operands)

    if cgen.AVX:
        line1 = "vdpps %s, %s, %s, 0x71 \n" % (reg1, reg1, reg2)
        code = code1 + code2 + line1
    elif cgen.SSE41:
        line1 = "dpps %s, %s, 0x71\n" % (reg1, reg2)
        code = code1 + code2 + line1
    else:  # SSE2 implementation
        line1 = "mulps %s, %s\n" % (reg1, reg2)
        line2 = "movhlps %s, %s\n" % (reg2, reg1)
        line3 = "addss %s, %s\n" % (reg1, reg2)
        line4 = "pshufd %s, %s, 1\n" % (reg2, reg1)
        line5 = "addss %s, %s\n" % (reg1, reg2)
        code = code1 + code2 + line1 + line2 + line3 + line4 + line5

    cgen.release_reg(reg2)
    return code, reg1, FloatArg

register_function('dot', _dot_function, inline=True)


def _normalize_function(cgen, operands):
    if len(operands) != 1:
        raise ValueError("Two many operands in normalize func.", operands)
    code1, reg1, typ1 = load_operand(cgen, operands[0])
    if typ1 != Vec3Arg:
        raise ValueError("Type mismatch in normalize function", operands[0])

    tmp1 = cgen.register(typ='xmm')
    tmp2 = cgen.register(typ='xmm')

    if cgen.AVX:
        l1 = "vdpps %s, %s, %s, 0x7f \n" % (tmp1, reg1, reg1)
        l2 = "vsqrtps %s, %s\n" % (tmp1, tmp1)
        l3 = "vdivps %s, %s, %s\n" % (reg1, reg1, tmp1)
        code = code1 + l1 + l2 + l3
    elif cgen.SSE41:
        l1 = "movaps %s, %s\n" % (tmp1, reg1)
        l2 = "dpps %s, %s, 0x7f\n" % (tmp1, tmp1)
        l3 = "sqrtps %s, %s\n" % (tmp1, tmp1)
        l4 = 'divps %s, %s\n' % (reg1, tmp1)
        code = code1 + l1 + l2 + l3 + l4
    else:  # SSE2 implementation
        l1 = "movaps %s, %s\n" % (tmp2, reg1)
        l2 = "mulps %s, %s\n" % (tmp2, tmp2)
        l3 = "movhlps %s, %s\n" % (tmp1, tmp2)
        l4 = "addss %s, %s\n" % (tmp2, tmp1)
        l5 = "pshufd %s, %s, 1\n" % (tmp1, tmp2)
        l6 = "addss %s, %s\n" % (tmp2, tmp1)
        l7 = "shufps %s, %s, 0x00\n" % (tmp2, tmp2)
        l8 = "sqrtps %s, %s\n" % (tmp2, tmp2)
        l9 = 'divps %s, %s\n' % (reg1, tmp2)
        code = code1 + l1 + l2 + l3 + l4 + l5 + l6 + l7 + l8 + l9

    cgen.release_reg(tmp1)
    cgen.release_reg(tmp2)
    return code, reg1, Vec3Arg

register_function('normalize', _normalize_function, inline=True)


def _cross_function(cgen, operands):
    if len(operands) != 2:
        raise ValueError("Wrong number of arguments in corss func.", operands)
    code1, xmm1, typ1 = load_operand(cgen, operands[0])
    code2, xmm2, typ2 = load_operand(cgen, operands[1])

    if typ1 != Vec3Arg or typ2 != Vec3Arg:
        raise ValueError("Cross expecte two Vec3Arg arguments.", operands)

    tmp1 = cgen.register(typ='xmm')
    tmp2 = cgen.register(typ='xmm')

    if cgen.AVX:
        l1 = "vmovaps %s, %s\n" % (tmp1, xmm1)
        l2 = "vmovaps %s, %s\n" % (tmp2, xmm2)
        l3 = "vshufps %s, %s, %s, 0xC9\n" % (xmm1, xmm1, xmm1)
        l4 = "vshufps %s, %s, %s, 0xD2\n" % (xmm2, xmm2, xmm2)
        l5 = "vmulps %s, %s, %s\n" % (xmm1, xmm1, xmm2)
        l6 = "vshufps %s, %s, %s, 0xD2\n" % (tmp1, tmp1, tmp1)
        l7 = "vshufps %s, %s, %s, 0xC9\n" % (tmp2, tmp2, tmp2)
        l8 = "vmulps %s, %s, %s\n" % (tmp1, tmp1, tmp2)
        l9 = "vsubps %s, %s, %s\n" % (xmm1, xmm1, tmp1)
    else:
        l1 = "movaps %s, %s\n" % (tmp1, xmm1)
        l2 = "movaps %s, %s\n" % (tmp2, xmm2)
        l3 = "shufps %s, %s, 0xC9\n" % (xmm1, xmm1)
        l4 = "shufps %s, %s, 0xD2\n" % (xmm2, xmm2)
        l5 = "mulps %s, %s\n" % (xmm1, xmm2)
        l6 = "shufps %s, %s, 0xD2\n" % (tmp1, tmp1)
        l7 = "shufps %s, %s, 0xC9\n" % (tmp2, tmp2)
        l8 = "mulps %s, %s\n" % (tmp1, tmp2)
        l9 = "subps %s, %s\n" % (xmm1, tmp1)

    cgen.release_reg(xmm2)
    cgen.release_reg(tmp1)
    cgen.release_reg(tmp2)
    code = code1 + code2 + l1 + l2 + l3 + l4 + l5 + l6 + l7 + l8 + l9
    return code, xmm1, Vec3Arg

register_function('cross', _cross_function, inline=True)

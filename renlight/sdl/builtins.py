
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

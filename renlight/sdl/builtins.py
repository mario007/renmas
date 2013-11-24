
from .strs import Name, Attribute, Const
from .args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg, StructArg,\
    SampledArg, RGBArg
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


def _sqrt(cgen, operands):
    if len(operands) != 1:
        raise ValueError("Wrong number of arguments in sqrt func.", operands)

    code1, xmm1, typ1 = load_operand(cgen, operands[0])

    #TODO --- typ1 == Integer
    if typ1 == FloatArg:
        if cgen.AVX:
            code1 += 'vsqrtss %s, %s, %s\n' % (xmm1, xmm1, xmm1)
        else:
            code1 += 'sqrtss %s, %s\n' % (xmm1, xmm1)
    elif typ1 == Vec2Arg or typ1 == Vec3Arg or typ1 == Vec4Arg:
        if cgen.AVX:
            code1 += 'vsqrtps %s, %s, %s\n' % (xmm1, xmm1, xmm1)
        else:
            code1 += 'sqrtps %s, %s\n' % (xmm1, xmm1)
    else:
        raise ValueError("Unsuported type of argument in sqrt function!", typ1)

    return code1, xmm1, typ1

register_function('sqrt', _sqrt, inline=True)


def _clock(cgen, operands):
    if len(operands) != 0:
        raise ValueError("Clock function doesnt accept arguments.", operands)

    reg = cgen.register(reg='eax')
    code = "cpuid\nrdtsc\n"

    return code, reg, IntArg

register_function('clock', _clock, inline=False)


def _get_rgba(cgen, operands):
    if len(operands) != 3:
        raise ValueError("Wrong number of args in get_rgba fucntion", operands)
    if not isinstance(operands[0], Name):  # TODO improve this
        raise ValueError("First operand must be Name!!!", operands[0])
    arg1 = cgen.get_arg(operands[0])
    if not isinstance(arg1, StructArg):
        raise ValueError("Image structure is expected!", arg1)
    if arg1.type_name != "ImagePRGBA" and arg1.type_name != 'ImageRGBA':
        raise ValueError("Wrong image structure!", arg1.type_name)
    code1, reg1, typ1 = load_operand(cgen, operands[1])
    code2, reg2, typ2 = load_operand(cgen, operands[2])

    if typ1 != IntArg or typ2 != IntArg:
        raise ValueError("Argument for x and y must be integers", typ1, typ2)

    code3, reg3, typ3 = load_operand(cgen, Attribute(arg1.name, 'pitch'))
    code4 = "imul %s, %s\n" % (reg2, reg3)
    if arg1.type_name == "ImagePRGBA":
        code5 = "imul %s, %s, 16\n" % (reg1, reg1)
    else:
        code5 = "imul %s, %s, 4\n" % (reg1, reg1)
    code6 = "add %s, %s\n" % (reg2, reg1)

    cgen.release_reg(reg1)
    cgen.release_reg(reg3)

    code7, reg4, typ4 = load_operand(cgen, Attribute(arg1.name, 'pixels'))

    if cgen.BIT64:
        code8 = "add %s, %s\n" % (reg4, 'r' + reg2[1:])  # TODO improve conv.
    else:
        code8 = "add %s, %s\n" % (reg4, reg2)

    xmm_reg = cgen.register(typ='xmm')
    if arg1.type_name == "ImagePRGBA":
        if cgen.AVX:
            code9 = "vmovaps %s, oword [%s]\n" % (xmm_reg, reg4)
        else:
            code9 = "movaps %s, oword [%s]\n" % (xmm_reg, reg4)
    else:
        con = Const((0.0039, 0.0039, 0.0039, 0.0039))
        arg = cgen.create_const(con)
        xmm_reg2 = cgen.register(typ='xmm')
        if cgen.AVX:
            code9 = "vmovss %s, dword [%s]\n" % (xmm_reg, reg4)
            code9 += "vpxor %s, %s, %s\n" % (xmm_reg2, xmm_reg2, xmm_reg2)
            code9 += "vpunpcklbw %s, %s, %s\n" % (xmm_reg, xmm_reg, xmm_reg2)
            code9 += "vpunpcklwd %s, %s, %s\n" % (xmm_reg, xmm_reg, xmm_reg2)
            code9 += "vcvtdq2ps %s, %s\n" % (xmm_reg, xmm_reg)
            code9 += "vmulps %s, %s, oword [%s]\n" % (xmm_reg, xmm_reg, arg.name)
        else:
            code9 = "movss %s, dword [%s]\n" % (xmm_reg, reg4)
            code9 += "pxor %s, %s\n" % (xmm_reg2, xmm_reg2)
            code9 += "punpcklbw %s, %s\n" % (xmm_reg, xmm_reg2)
            code9 += "punpcklwd %s, %s\n" % (xmm_reg, xmm_reg2)
            code9 += "cvtdq2ps %s, %s\n" % (xmm_reg, xmm_reg)
            code9 += "mulps %s, oword [%s]\n" % (xmm_reg, arg.name)

        cgen.release_reg(xmm_reg2)

    cgen.release_reg(reg2)
    cgen.release_reg(reg4)

    code = code1 + code2 + code3 + code4 + code5 + code6 + code7 + code8 + code9
    return code, xmm_reg, Vec4Arg

register_function('get_rgba', _get_rgba, inline=True)


def _set_rgba(cgen, operands):
    if len(operands) != 4:
        raise ValueError("Wrong number of args in set_rgba fucntion", operands)
    arg1 = cgen.get_arg(operands[0])
    if not isinstance(arg1, StructArg):
        raise ValueError("Image structure is expected!", arg1)
    if arg1.type_name != "ImagePRGBA":
        raise ValueError("Wrong image structure!", arg1.type_name)

    code1, reg1, typ1 = load_operand(cgen, operands[1])
    code2, reg2, typ2 = load_operand(cgen, operands[2])

    if typ1 != IntArg or typ2 != IntArg:
        raise ValueError("Argument for x and y must be integers", typ1, typ2)

    code3, reg3, typ3 = load_operand(cgen, Attribute(arg1.name, 'pitch'))

    code4 = "imul %s, %s\n" % (reg2, reg3)
    code5 = "imul %s, %s, 16\n" % (reg1, reg1)
    code6 = "add %s, %s\n" % (reg2, reg1)

    cgen.release_reg(reg1)
    cgen.release_reg(reg3)

    code7, reg4, typ4 = load_operand(cgen, Attribute(arg1.name, 'pixels'))
    if cgen.BIT64:
        code8 = "add %s, %s\n" % (reg4, 'r' + reg2[1:])  # TODO improve conv.
    else:
        code8 = "add %s, %s\n" % (reg4, reg2)

    code9, xmm_reg, typ5 = load_operand(cgen, operands[3])
    if typ5 != Vec4Arg:
        raise ValueError("Operand is expected to be Vec4 type", typ5)

    if cgen.AVX:
        code10 = "vmovaps oword [%s], %s\n" % (reg4, xmm_reg)
    else:
        code10 = "movaps oword [%s], %s\n" % (reg4, xmm_reg)

    cgen.release_reg(reg4)
    cgen.release_reg(xmm_reg)

    code = code1 + code2 + code3 + code4 + code5 + code6 + code7 + code8 + code9 + code10
    return code, reg2, IntArg

register_function('set_rgba', _set_rgba, inline=True)


def _sum_samples(cgen, operands):
    if len(operands) != 1:
        raise ValueError("Wrong number of arguments in sum_samples", operands)
    arg = cgen.get_arg(operands[0])
    if not isinstance(arg, SampledArg):
        raise ValueError("SampledArg is expected!", arg)

    n = len(arg.value.samples)
    if cgen.AVX:
        rounds = n // 8 - 1
        code = "vmovaps ymm0, yword[%s]\n" % arg.name
        offset = 32
        for i in range(rounds):
            code += "vaddps ymm0, ymm0, yword[%s + %i]\n" % (arg.name, offset)
            offset += 32
        code += """
            vperm2f128 ymm1, ymm0, ymm0, 0x01
            vaddps xmm0, xmm0, xmm1
            vmovhlps xmm2, xmm2, xmm0
            vmovaps xmm1, xmm0
            vshufps xmm1, xmm1, xmm1, 0x55
            vmovaps xmm3, xmm2
            vshufps xmm3, xmm3, xmm3, 0x55
            vaddss xmm0, xmm0, xmm1
            vaddss xmm2, xmm2, xmm3
            vaddss xmm0, xmm0, xmm2
            """
    else:
        rounds = n // 4 - 1
        code = "movaps xmm0, oword[%s]\n" % arg.name
        offset = 16
        for i in range(rounds):
            code += "addps xmm0, oword[%s + %i]\n" % (arg.name, offset)
            offset += 16
        code += """
            movhlps xmm2, xmm0
            movaps xmm1, xmm0
            shufps xmm1, xmm1, 0x55
            movaps xmm3, xmm2
            shufps xmm3, xmm3, 0x55
            addss xmm0, xmm1
            addss xmm2, xmm3
            addss xmm0, xmm2
            """

    return code, 'xmm0', FloatArg

register_function('sum_samples', _sum_samples, inline=False)


def _spectrum(cgen, operands):
    if len(operands) != 2:
        raise ValueError("Wrong number of arguments in Spectrum", operands)

    arg = cgen.get_arg(operands[0])
    if type(arg) != RGBArg and type(arg) != SampledArg:
        raise ValueError("RGBArg or SampledArg is expected", arg)
    code, xmm, typ2 = load_operand(cgen, operands[1])
    if typ2 != FloatArg:
        raise ValueError("FloatArg is expected", typ2)

    if cgen.AVX:
        code += "vshufps %s, %s, %s, 0x00\n" % (xmm, xmm, xmm)
    else:
        code += "shufps %s, %s, 0x00\n" % (xmm, xmm)

    if type(arg) == RGBArg:
        return code, xmm, RGBArg

    name = Name(cgen._generate_name('local'))
    sam_arg = cgen.create_arg(name, arg)
    dst_reg = cgen.register(typ='pointer')
    code += 'mov %s, %s\n' % (dst_reg, sam_arg.name)

    offset = 0
    if cgen.AVX:
        xmm = "y" + xmm[1:]
        code += "vperm2f128 %s, %s, %s, 0x00 \n" % (xmm, xmm, xmm)
        rounds = len(arg.value.samples) // 8
        for i in range(rounds):
            code += "vmovaps yword[%s + %i], %s\n" % (sam_arg.name, offset, xmm)
            offset += 32
    else:
        rounds = len(arg.value.samples) // 4
        for i in range(rounds):
            code += "movaps oword[%s + %i], %s\n" % (sam_arg.name, offset, xmm)
            offset += 16

    code1, reg, typ = load_operand(cgen, name)
    return code + code1, reg, typ

register_function('Spectrum', _spectrum, inline=True)


def _call_indirect(cgen, operands):
    pass
    raise ValueError("Tu smo")

register_function('call_indirect', _call_indirect, inline=False)


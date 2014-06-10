
from .spectrum import RGBSpectrum, SampledSpectrum
from .strs import Name, Attribute, Const
from .args import IntArg, FloatArg, Vec2Arg, Vec3Arg, Vec4Arg, StructArg,\
    SampledArg, RGBArg, PointerArg
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


def _rgb_function(cgen, operands):
    if len(operands) != 3:
        raise ValueError("Wrong number of operands in rgb func.", operands)

    code1, xmm = _combine_two_floats(cgen, operands[0], operands[1])
    code2, xmm = _add_float(cgen, xmm, operands[2], 8)
    return code1 + code2, xmm, RGBArg

register_function('rgb', _rgb_function, inline=True)


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

    if cgen.AVX:
        code3 = "vshufps %s, %s, %s, 0xC9\n" % (tmp1, xmm1, xmm1)
        code3 += "vmulps %s, %s, %s\n" % (tmp1, tmp1, xmm2)
        code3 += "vshufps %s, %s, %s, 0xC9\n" % (xmm2, xmm2, xmm2)
        if cgen.FMA:
            code3 += 'vfmsub132ps %s, %s, %s\n' % (xmm2, tmp1, xmm1)
        else:
            code3 += "vmulps %s, %s, %s\n" % (xmm2, xmm2, xmm1)
            code3 += "vsubps %s, %s, %s\n" % (xmm2, xmm2, tmp1)
        code3 += "vshufps %s, %s, %s, 0xC9\n" % (xmm2, xmm2, xmm2)
    else:
        code3 = "movaps %s, %s\n" % (tmp1, xmm1)
        code3 += "shufps %s, %s, 0xC9\n" % (xmm1, xmm1)
        code3 += "mulps %s, %s\n" % (xmm1, xmm2)
        code3 += "shufps %s, %s, 0xC9\n" % (xmm2, xmm2)
        code3 += "mulps %s, %s\n" % (xmm2, tmp1)
        code3 += "subps %s, %s\n" % (xmm2, xmm1)
        code3 += "shufps %s, %s, 0xC9\n" % (xmm2, xmm2)

    cgen.release_reg(xmm1)
    cgen.release_reg(tmp1)
    code = code1 + code2 + code3
    return code, xmm2, Vec3Arg

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
    if len(operands) != 1:
        raise ValueError("Wrong number of arguments in Spectrum", operands)

    code, xmm, typ1 = load_operand(cgen, operands[0])
    if typ1 != FloatArg:
        raise ValueError("FloatArg is expected", typ1)

    if cgen.AVX:
        code += "vshufps %s, %s, %s, 0x00\n" % (xmm, xmm, xmm)
    else:
        code += "shufps %s, %s, 0x00\n" % (xmm, xmm)

    if cgen.color_mgr:
        spec = cgen.color_mgr.zero()
    else:
        spec = RGBSpectrum(0.0, 0.0, 0.0)
    if isinstance(spec, RGBSpectrum):
        return code, xmm, RGBArg

    name = Name(cgen._generate_name('local'))
    sam_arg = cgen.create_arg(name, SampledArg)
    dst_reg = cgen.register(typ='pointer')
    code += 'mov %s, %s\n' % (dst_reg, sam_arg.name)

    offset = 0
    if cgen.AVX:
        xmm = "y" + xmm[1:]
        code += "vperm2f128 %s, %s, %s, 0x00 \n" % (xmm, xmm, xmm)
        rounds = len(spec.samples) // 8
        for i in range(rounds):
            code += "vmovaps yword[%s + %i], %s\n" % (sam_arg.name, offset, xmm)
            offset += 32
    else:
        rounds = len(spec.samples) // 4
        for i in range(rounds):
            code += "movaps oword[%s + %i], %s\n" % (sam_arg.name, offset, xmm)
            offset += 16

    code1, reg, typ = load_operand(cgen, name)
    return code + code1, reg, typ


register_function('Spectrum', _spectrum, inline=True)


def _label_sufix(AVX=False, BIT64=False):
    avx = 'avx' if AVX else 'sse'
    bit = '64' if BIT64 else '32'
    suffix = '%s_%s' % (avx, bit)
    return suffix


def _math_fun(cgen, operands, fun_ss, fun_ps):
    if len(operands) != 1:
        msg = "Wrong number of arguments in %s, %s fucntion" % (fun_ss, fun_ps)
        raise ValueError(msg, operands)

    xmm1 = cgen.register(reg='xmm0')
    code1, reg1, typ1 = load_operand(cgen, operands[0], dest_reg=xmm1)

    sufix = _label_sufix(cgen.AVX, cgen.BIT64)
    if typ1 == FloatArg:
        label = '%s_%s_yxa8m3epu' % (fun_ss, sufix)
        cgen.add_ext_function(fun_ss, label)
    elif typ1 == Vec2Arg or typ1 == Vec3Arg or typ1 == Vec4Arg:
        label = '%s_%s_pxp3axmuj' % (fun_ps, sufix)
        cgen.add_ext_function(fun_ps, label)
    else:
        raise ValueError("Unsuported type for math function", typ1)
    code2 = 'call %s\n' % label
    code3 = code1 + code2
    return code3, 'xmm0', typ1


def _log(cgen, operands):
    return _math_fun(cgen, operands, 'log_ss', 'log_ps')

register_function('log', _log, inline=False)


def _exp(cgen, operands):
    return _math_fun(cgen, operands, 'exp_ss', 'exp_ps')

register_function('exp', _exp, inline=False)


def _acos(cgen, operands):
    return _math_fun(cgen, operands, 'acos_ss', 'acos_ps')

register_function('acos', _acos, inline=False)


def _asin(cgen, operands):
    return _math_fun(cgen, operands, 'asin_ss', 'asin_ps')

register_function('asin', _asin, inline=False)


def _atan(cgen, operands):
    return _math_fun(cgen, operands, 'atan_ss', 'atan_ps')

register_function('atan', _atan, inline=False)


def _cos(cgen, operands):
    return _math_fun(cgen, operands, 'cos_ss', 'cos_ps')

register_function('cos', _cos, inline=False)


def _sin(cgen, operands):
    return _math_fun(cgen, operands, 'sin_ss', 'sin_ps')

register_function('sin', _sin, inline=False)


def _tan(cgen, operands):
    return _math_fun(cgen, operands, 'tan_ss', 'tan_ps')

register_function('tan', _tan, inline=False)


def _math_atanr2_pow(cgen, operands, fun_ss, fun_ps):
    if len(operands) != 2:
        msg = "Wrong number of arguments in %s, %s fucntion" % (fun_ss, fun_ps)
        raise ValueError(msg, operands)

    xmm1 = cgen.register(reg='xmm0')
    xmm2 = cgen.register(reg='xmm1')
    code1, reg1, typ1 = load_operand(cgen, operands[0], dest_reg=xmm1)
    code2, reg2, typ2 = load_operand(cgen, operands[1], dest_reg=xmm2)

    if typ1 != typ2:
        raise ValueError("Type mismatch atanr2 function!", typ1, typ2)

    sufix = _label_sufix(cgen.AVX, cgen.BIT64)
    if typ1 == FloatArg:
        label = '%s_%s_yxa8m3epu' % (fun_ss, sufix)
        cgen.add_ext_function(fun_ss, label)
    elif typ1 == Vec2Arg or typ1 == Vec3Arg or typ1 == Vec4Arg:
        label = '%s_%s_pxp3axmuj' % (fun_ps, sufix)
        cgen.add_ext_function(fun_ps, label)
    else:
        raise ValueError("Unsuported type for math function", typ1)

    code3 = 'call %s\n' % label
    code4 = code1 + code2 + code3
    cgen.release_reg(reg2)
    return code4, 'xmm0', typ1


def _pow(cgen, operands):
    return _math_atanr2_pow(cgen, operands, 'pow_ss', 'pow_ps')

register_function('pow', _pow, inline=False) 


def _atanr2(cgen, operands):
    return _math_atanr2_pow(cgen, operands, 'atanr2_ss', 'atanr2_ps')

register_function('atanr2', _atanr2, inline=False) 


def _rand_int(cgen, operands):
    if len(operands) != 0:
        raise ValueError("Function doesn't accept arguments", operands)

    label = 'rand_int_pup9aixpmyj'
    cgen.add_ext_function('rand_int', label)

    code = 'call %s\n' % label
    #Note: random function returns 32-bit unsigned number and we
    #want 32-bit signed number but only positive, so we calculate abs value
    code += 'mov ebx, eax\n'
    code += 'neg eax\n'
    code += 'cmovl eax, ebx\n'
    return code, 'eax', IntArg

register_function('rand_int', _rand_int, inline=False)

def _rand1234(cgen, operands, prefix, ret_type):
    if len(operands) != 0:
        raise ValueError("Function doesn't accept arguments", operands)
    label = '%s_pup9aixpmyj' % prefix
    cgen.add_ext_function('random', label)
    code = 'call %s\n' % label
    return code, 'xmm0', ret_type

def _random(cgen, operands):
    return _rand1234(cgen, operands, 'random', FloatArg)


register_function('random', _random, inline=False)


def _random2(cgen, operands):
    return _rand1234(cgen, operands, 'random2', Vec2Arg)


register_function('random2', _random2, inline=False)


def _random3(cgen, operands):
    return _rand1234(cgen, operands, 'random3', Vec3Arg)


register_function('random3', _random3, inline=False)


def _random4(cgen, operands):
    return _rand1234(cgen, operands, 'random4', Vec4Arg)


register_function('random4', _random4, inline=False)


def _min_max(cgen, operands, inst='max'):
    if len(operands) != 2:
        msg = "Wrong number of arguments in %s function." % inst
        raise ValueError(msg, operands)

    code1, xmm1, typ1 = load_operand(cgen, operands[0])
    code2, xmm2, typ2 = load_operand(cgen, operands[1])

    if typ1 != typ2:
        raise ValueError("Arguments must be of the same type in min max function!",
                typ1, typ2)

    if typ1 == FloatArg:
        if cgen.AVX:
            l1 = 'v%sss %s, %s, %s\n' % (inst, xmm1, xmm1, xmm2)
        else:
            l1 = '%sss %s, %s\n' % (inst, xmm1, xmm2)
    elif typ1 == Vec2Arg or typ1 == Vec3Arg or typ1 == Vec4Arg:
        if cgen.AVX:
            l1 = 'v%sps %s, %s, %s\n' % (inst, xmm1, xmm1, xmm2)
        else:
            l1 = '%sps %s, %s\n' % (inst, xmm1, xmm2)
    else:
        raise ValueError("Unsuported type of argument in min max function!", typ1)

    cgen.release_reg(xmm2)

    code = code1 + code2 + l1
    return code, xmm1, typ1


def _max(cgen, operands):
    return _min_max(cgen, operands, 'max')


register_function('max', _max, inline=True)


def _min(cgen, operands):
    return _min_max(cgen, operands, 'min')


register_function('min', _min, inline=True)


def _resolve(cgen, operands):
    if len(operands) != 2:
        msg = "Wrong number of arguments in resolve function."
        raise ValueError(msg, operands)

    code1, reg, typ1 = load_operand(cgen, operands[0])
    if typ1 != PointerArg:
        raise ValueError("First arugment in resolve function must be pointer!", operands[0])
    if not isinstance(operands[1], Name):
        raise ValueError("Second argument must be Name in resolve!", operands[1])

    if operands[1].name == 'int':
        reg2 = cgen.register(typ='general')
        code2 = 'mov %s, dword [%s]\n' % (reg2, reg) 
        cgen.release_reg(reg)
        return code1 + code2, reg2, IntArg
    elif operands[1].name in ('vec2', 'vec3', 'vec4'):
        xmm = cgen.register(typ='xmm')
        ret_type = {'vec2': Vec2Arg, 'vec3': Vec3Arg, 'vec4': Vec4Arg}
        if cgen.AVX:
            code2 = "vmovaps %s, oword[%s]\n" % (xmm, reg)
        else:
            code2 = "movaps %s, oword[%s]\n" % (xmm, reg)
        cgen.release_reg(reg)
        return code1 + code2, xmm, ret_type[operands[1].name]
    else:
        raise ValueError("%s type not yet supported in resolve!" % operands[1].name)
    

register_function('resolve', _resolve, inline=True)


def _abs(cgen, operands):
    if len(operands) != 1:
        msg = "Wrong number of arguments in abs function."
        raise ValueError(msg, operands)

    code, reg, typ = load_operand(cgen, operands[0])
    if typ == IntArg:
        reg2 = cgen.register(typ='general')
        code += 'mov %s, %s\n' % (reg2, reg)
        code += 'neg %s\n' % reg
        code += 'cmovl %s, %s\n' % (reg, reg2)
        cgen.release_reg(reg2)
        return code, reg, IntArg
    elif typ == FloatArg or typ == Vec2Arg or typ == Vec3Arg or typ == Vec4Arg:
        xmm = cgen.register(typ='xmm')
        if cgen.AVX:
            code += 'vpcmpeqw %s, %s, %s\n' % (xmm, xmm, xmm)
            code += 'vpsrld %s, %s, 1\n' % (xmm, xmm)
            code += 'vandps %s, %s, %s\n' % (reg, reg, xmm)
        else:
            code += 'pcmpeqw %s, %s\n' % (xmm, xmm)
            code += 'psrld %s, 1\n' % xmm
            code += 'andps %s, %s\n' % (reg, xmm)
        cgen.release_reg(xmm)
        return code, reg, typ
    else:
        raise ValueError("Type not yet supported in abs function!", typ1)


register_function('abs', _abs, inline=True)

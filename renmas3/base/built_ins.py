import platform
import renmas3.switch as proc

from .arg import Attribute
from .integer import Integer, Float
from .vec234 import Vec2, Vec3, Vec4
from .usr_type import Struct
from .arg import conv_float_to_int, conv_int_to_float

from .instr import load_operand
from .cgen import register_function
from .spec import RGBSpec, SampledSpec

def _int_function(cgen, args):
    if len(args) == 0:
        reg = cgen.register(typ='general')
        code = "xor %s, %s\n" % (reg, reg)
        return code, reg, Integer
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in int function", args)
    code, reg, typ = load_operand(cgen, args[0])
    if typ == Integer:
        return code, reg, typ
    elif typ == Float:
        to_reg = cgen.register(typ="general")
        code += conv_float_to_int(cgen, to_reg, reg)
        cgen.release_reg(reg)
        return code, to_reg, Integer
    else:
        raise ValueError("Unsuported argument type", args[0])

register_function('int', _int_function, inline=True) 

def _float_function(cgen, args):
    if len(args) == 0:
        xmm = cgen.register(typ='xmm')
        if cgen.AVX:
            code = "vpxor %s, %s, %s\n" % (xmm, xmm, xmm)
        else:
            code = "pxor %s, %s\n" % (xmm, xmm)
        return code, xmm, Float
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in int function", args)
    code, reg, typ = load_operand(cgen, args[0])
    if typ == Float:
        return code, reg, typ
    elif typ == Integer:
        xmm = cgen.register(typ='xmm')
        code += conv_int_to_float(cgen, reg, xmm)
        cgen.release_reg(reg)
        return code, xmm, Float 
    else:
        raise ValueError("Unsuported argument type", args[0])

register_function('float', _float_function, inline=True) 

def _combine_two_floats(cgen, arg1, arg2):
    xmm1 = cgen.register(typ='xmm')
    xmm2 = cgen.register(typ='xmm')
    if cgen.AVX:
        code0 = "vpxor %s, %s, %s\n" % (xmm2, xmm2, xmm2)
        code0 += "vpxor %s, %s, %s\n" % (xmm1, xmm1, xmm1)
    else:
        code0 = "pxor %s, %s\n" % (xmm2, xmm2)
        code0 += "pxor %s, %s\n" % (xmm1, xmm1)
    code1, reg1, typ1 = load_operand(cgen, arg1, dest_reg=xmm1)
    code2, reg2, typ2 = load_operand(cgen, arg2, dest_reg=xmm2)

    if typ1 != Float or typ2 != Float:
        raise ValueError("Arguments must be floats!", typ1, typ2)

    if cgen.AVX:
        code3 = "vpslldq %s, %s, 4\n" % (xmm2, xmm2)
        code4 = "vorps %s, %s, %s\n" % (xmm1, xmm1, xmm2)
    else:
        code3 = "pslldq %s, 4\n" % xmm2
        code4 = "orps %s, %s\n" % (xmm1, xmm2)
    cgen.release_reg(xmm2)
    code = code0 + code1 + code2 + code3 + code4
    return code, xmm1

def _add_float(cgen, xmm, arg, offset):
    xmm2 = cgen.register(typ='xmm')
    if cgen.AVX:
        code = "vpxor %s, %s, %s\n" % (xmm2, xmm2, xmm2)
    else:
        code = "pxor %s, %s\n" % (xmm2, xmm2)
    code1, reg1, typ1 = load_operand(cgen, arg, dest_reg=xmm2)
    if typ1 != Float:
        raise ValueError("Argument must be floats!", typ1)
    if cgen.AVX:
        code2 = "vpslldq %s, %s, %i\n" % (xmm2, xmm2, offset)
        code3 = "vorps %s, %s, %s\n" % (xmm, xmm, xmm2)
    else:
        code2 = "pslldq %s, %i\n" % (xmm2, offset)
        code3 = "orps %s, %s\n" % (xmm, xmm2)
    cgen.release_reg(xmm2)
    code = code + code1 + code2 + code3
    return code, xmm


def _float2_function(cgen, args):
    if len(args) != 2:
        raise ValueError("Wrong number of arguments in float2 function", args)

    code, xmm = _combine_two_floats(cgen, args[0], args[1])
    return code, xmm, Vec2 

register_function('float2', _float2_function, inline=True) 

def _float3_function(cgen, args):
    if len(args) != 3:
        raise ValueError("Wrong number of arguments in float3 function", args)

    code1, xmm = _combine_two_floats(cgen, args[0], args[1])
    code2, xmm = _add_float(cgen, xmm, args[2], 8)
    return code1 + code2, xmm, Vec3 

register_function('float3', _float3_function, inline=True) 

def _float4_function(cgen, args):
    if len(args) != 4:
        raise ValueError("Wrong number of arguments in float3 function", args)

    code1, xmm = _combine_two_floats(cgen, args[0], args[1])
    code2, xmm = _add_float(cgen, xmm, args[2], 8)
    code3, xmm = _add_float(cgen, xmm, args[3], 12)
    return code1 + code2 + code3, xmm, Vec4 

register_function('float4', _float4_function, inline=True) 

def _spectrum_to_rgb(cgen, args):
    if len(args) != 1:
        raise ValueError("Function accept just one arguement!", args)

    cgen.clear_regs()
    if cgen.BIT64:
        reg = cgen.register(typ='general', bit=64, reg='rax')
    else:
        reg = cgen.register(typ='general', bit=32, reg='eax')

    code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=reg)
    if typ1 != RGBSpec and typ1 != SampledSpec:
        raise ValueError("Spectrum argument is expected!", args[0])

    label = 'spectrum_to_rgb_yxmpa1y5z0p'
    cgen.add_color_func('spectrum_to_rgb', label)
    call = 'call %s\n' % label

    code = code1 +  call
    return code, 'xmm0', Vec3


register_function('spectrum_to_rgb', _spectrum_to_rgb, inline=False) 

def _rgb_to_spectrum(cgen, args):
    if len(args) != 1:
        raise ValueError("Function accept just one arguement!", args)

    cgen.clear_regs()
    if cgen.BIT64:
        reg = cgen.register(typ='general', bit=64, reg='rax')
    else:
        reg = cgen.register(typ='general', bit=32, reg='eax')
    arg = cgen.create_tmp_spec()
    code1, reg1, typ1 = arg.load_cmd(cgen, dest_reg=reg)

    xmm = cgen.register(typ='xmm', reg='xmm0')
    code2, reg2, typ2 = load_operand(cgen, args[0], dest_reg=xmm)

    if typ2 != Vec3 and typ2 != Vec4:
        raise ValueError("Vector3 or Vector4 argument is expected!", args[0])

    label = 'rgb_to_spectrum_yxmpa1y5z0p'
    cgen.add_color_func('rgb_to_spectrum', label)
    call = 'call %s\n' % label

    cgen.release_reg(xmm)

    code = code1 + code2 + call
    return code, reg, typ1 

register_function('rgb_to_spectrum', _rgb_to_spectrum, inline=False) 

def _chromacity_to_spectrum(cgen, args):
    if len(args) != 2:
        raise ValueError("Function accept two arguements!", args)
    cgen.clear_regs()
    xmm1 = cgen.register(reg='xmm0')
    xmm2 = cgen.register(reg='xmm1')
    code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=xmm1)
    code2, reg2, typ2 = load_operand(cgen, args[1], dest_reg=xmm2)

    if typ1 != Float or typ2 != Float:
        raise ValueError("Type mismatch! Float arugment is expected.", args)

    if cgen.BIT64:
        reg3 = cgen.register(typ='general', bit=64, reg='rax')
    else:
        reg3 = cgen.register(typ='general', bit=32, reg='eax')
    arg = cgen.create_tmp_spec()
    code3, reg3, typ3 = arg.load_cmd(cgen, dest_reg=reg3)

    label = 'chromacity_to_spectrum_yxmpa1y5z0p'
    cgen.add_color_func('chromacity_to_spectrum', label)
    call = 'call %s\n' % label

    cgen.release_reg(xmm1)
    cgen.release_reg(xmm2)
    code = code1 + code2 + code3 + call
    return code, reg3, typ3

register_function('chromacity_to_spectrum', _chromacity_to_spectrum, inline=False) 

def _luminance(cgen, args):
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in normalize fucntion", args)

    cgen.clear_regs()

    #TODO FIXME get_arg return struct if argument is attribute
    s_arg = cgen.get_arg(args[0])
    if isinstance(s_arg, RGBSpec) or isinstance(s_arg, SampledSpec):
        if cgen.BIT64:
            reg1 = cgen.register(typ='general', bit=64, reg='rax')
        else:
            reg1 = cgen.register(typ='general', bit=32, reg='eax')
        code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=reg1)
        label = 'luminance_yxmpa1y5z0p'
        cgen.add_color_func('luminance', label)
        call = 'call %s\n' % label
        code = code1 + call
        return code, 'xmm0', Float

    code1, reg1, typ1 = load_operand(cgen, args[0])
    if typ1 != Vec3 and typ1 != Vec4:
        raise ValueError("Type mismatch in luminance function", typ1)

    arg = cgen.create_const((0.2126, 0.7152, 0.0722))

    tmp1 = cgen.register(typ='xmm')

    if cgen.AVX:
        line1 = "vmovaps %s, oword [%s]\n" % (tmp1, arg.name)
        line2 = "vdpps %s, %s, %s, 0x71 \n" % (reg1, reg1, tmp1)
        code = code1 + line1 + line2
    elif proc.SSE41:
        line1 = "movaps %s, oword [%s]\n" % (tmp1, arg.name)
        line2 = "dpps %s, %s, 0x71\n" % (reg1, tmp1)
        code = code1 + line1 + line2
    else: #SSE2 implementation
        line1 = "movaps %s, oword [%s]\n" % (tmp1, arg.name)
        line2 = "mulps %s, %s\n" % (reg1, tmp1)
        line3 = "movhlps %s, %s\n" % (tmp1, reg1)
        line4 = "addss %s, %s\n" % (reg1, tmp1)
        line5 = "pshufd %s, %s, 1\n" % (tmp1, reg1)
        line6 = "addss %s, %s\n" % (reg1, tmp1)
        code = code1 + line1 + line2 + line3 + line4 + line5 + line6

    cgen.release_reg(tmp1)
    return code, reg1, Float

register_function('luminance', _luminance, inline=False) 

def _dot_function(cgen, args):
    if len(args) != 2:
        raise ValueError("Wrong number of arguments in dot fucntion", args)
    code1, reg1, typ1 = load_operand(cgen, args[0])
    code2, reg2, typ2 = load_operand(cgen, args[1])
    if typ1 != Vec3 or typ2 != Vec3:
        raise ValueError("Two Vec3 argument is expected to dot function", args)

    if cgen.AVX:
        line1 = "vdpps %s, %s, %s, 0x71 \n" % (reg1, reg1, reg2)
        code = code1 + code2 + line1
    elif proc.SSE41:
        line1 = "dpps %s, %s, 0x71\n" % (reg1, reg2)
        code = code1 + code2 + line1
    else: #SSE2 implementation
        line1 = "mulps %s, %s\n" % (reg1, reg2)
        line2 = "movhlps %s, %s\n" % (reg2, reg1)
        line3 = "addss %s, %s\n" % (reg1, reg2)
        line4 = "pshufd %s, %s, 1\n" % (reg2, reg1)
        line5 = "addss %s, %s\n" % (reg1, reg2)
        code = code1 + code2 + line1 + line2 + line3 + line4 + line5
    return code, reg1, Float

register_function('dot', _dot_function, inline=True) 

def _normalize_function(cgen, args):
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in normalize fucntion", args)
    code1, reg1, typ1 = load_operand(cgen, args[0])
    if typ1 != Vec3:
        raise ValueError("Type mismatch in normalize function", args[0])
    
    tmp1 = cgen.register(typ='xmm')
    tmp2 = cgen.register(typ='xmm')

    if proc.AVX:
        line1 = "vdpps %s, %s, %s, 0x7f \n" % (tmp1, reg1, reg1)
        line2 = "vsqrtps %s, %s\n" % (tmp1, tmp1)
        line3 = "vdivps %s, %s, %s\n" % (reg1, reg1, tmp1)
        code = code1 + line1 + line2 + line3
    elif proc.SSE41:
        line1 = "movaps %s, %s\n" % (tmp1, reg1)
        line2 = "dpps %s, %s, 0x7f\n" % (tmp1, tmp1)
        line3 = "sqrtps %s, %s\n" % (tmp1, tmp1)
        line4 = 'divps %s, %s\n' % (reg1, tmp1)
        code = code1 + line1 + line2 + line3 + line4
    else: #SSE2 implementation
        line1 = "movaps %s, %s\n" % (tmp2, reg1)
        line2 = "mulps %s, %s\n" % (tmp2, tmp2)
        line3 = "movhlps %s, %s\n" % (tmp1, tmp2)
        line4 = "addss %s, %s\n" % (tmp2, tmp1)
        line5 = "pshufd %s, %s, 1\n" % (tmp1, tmp2)
        line6 = "addss %s, %s\n" % (tmp2, tmp1)
        line7 = "shufps %s, %s, 0x00\n" % (tmp2, tmp2)
        line8 = "sqrtps %s, %s\n" % (tmp2, tmp2)
        line9 = 'divps %s, %s\n' % (reg1, tmp2)
        code = code1 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9

    cgen.release_reg(tmp1)
    cgen.release_reg(tmp2)
    return code, reg1, Vec3

register_function('normalize', _normalize_function, inline=True) 

def _get_rgba(cgen, args):
    if len(args) != 3:
        raise ValueError("Wrong number of arguments in get_rgb fucntion", args)
    arg1 = cgen.get_arg(args[0])
    if not isinstance(arg1, Struct):
        raise ValueError("Image structure is expected.", arg1)
    if arg1.typ.typ != "ImagePRGBA" and arg1.typ.typ != 'ImageRGBA':
        raise ValueError("Wrong image format", arg1.typ.typ)
    code1, reg1, typ1 = load_operand(cgen, args[1])
    code2, reg2, typ2 = load_operand(cgen, args[2])
    if typ1 != Integer or typ2 != Integer:
        raise ValueError("Argument for x and y must be integers", typ1, typ2)

    code3, reg3, typ3 = load_operand(cgen, Attribute(arg1.name, 'pitch'))
    code4 = "imul %s, %s\n" % (reg2, reg3)
    if arg1.typ.typ == "ImagePRGBA":
        code5 = "imul %s, %s, 16\n" % (reg1, reg1) 
    else:
        code5 = "imul %s, %s, 4\n" % (reg1, reg1) 
    code6 = "add %s, %s\n" % (reg2, reg1)

    cgen.release_reg(reg1)
    cgen.release_reg(reg3)

    code7, reg4, typ4 = load_operand(cgen, Attribute(arg1.name, 'pixels'))
    if cgen.BIT64:
        code8 = "add %s, %s\n" % (reg4, 'r' + reg2[1:]) #TODO better handle conversion of 32 and 64 registers
    else:
        code8 = "add %s, %s\n" % (reg4, reg2)

    xmm_reg = cgen.register(typ='xmm')
    if arg1.typ.typ == "ImagePRGBA":
        if cgen.AVX:
            code9 = "vmovaps %s, oword [%s]\n" % (xmm_reg, reg4)
        else:
            code9 = "movaps %s, oword [%s]\n" % (xmm_reg, reg4)
    else:
        arg = cgen.create_const((0.0039, 0.0039, 0.0039, 0.0039))
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
    return code, xmm_reg, Vec4

register_function('get_rgba', _get_rgba, inline=True) 

def _set_rgba(cgen, args):
    if len(args) != 4:
        raise ValueError("Wrong number of arguments in get_rgb fucntion", args)
    arg1 = cgen.get_arg(args[0])
    if not isinstance(arg1, Struct):
        raise ValueError("Image structure is expected.", arg1)
    if arg1.typ.typ != "ImagePRGBA":
        raise ValueError("Wrong image format", arg1.typ.typ)

    code1, reg1, typ1 = load_operand(cgen, args[1])
    code2, reg2, typ2 = load_operand(cgen, args[2])
    if typ1 != Integer or typ2 != Integer:
        raise ValueError("Argument for x and y must be integers", typ1, typ2)

    code3, reg3, typ3 = load_operand(cgen, Attribute(arg1.name, 'pitch'))
    code4 = "imul %s, %s\n" % (reg2, reg3)
    code5 = "imul %s, %s, 16\n" % (reg1, reg1) 
    code6 = "add %s, %s\n" % (reg2, reg1)

    cgen.release_reg(reg1)
    cgen.release_reg(reg3)

    code7, reg4, typ4 = load_operand(cgen, Attribute(arg1.name, 'pixels'))
    if cgen.BIT64:
        code8 = "add %s, %s\n" % (reg4, 'r' + reg2[1:]) #TODO better handle conversion of 32 and 64 registers
    else:
        code8 = "add %s, %s\n" % (reg4, reg2)

    code9, xmm_reg, typ5 = load_operand(cgen, args[3])
    if typ5 != Vec4:
        raise ValueError("Operand is expected to be Vec4 type", typ5)

    if proc.AVX:
        code10 = "vmovaps oword [%s], %s\n" % (reg4, xmm_reg)
    else:
        code10 = "movaps oword [%s], %s\n" % (reg4, xmm_reg)

    #cgen.release_reg(reg2)
    cgen.release_reg(reg4)
    cgen.release_reg(xmm_reg)

    code = code1 + code2 + code3 + code4 + code5 + code6 + code7 + code8 + code9 + code10
    return code, reg2, Integer

register_function('set_rgba', _set_rgba, inline=True) 

def _set_sampled_spec(cgen, reg, xmm):
    path = "Spectrum.values"
    n = cgen.nsamples()
    offset = 0
    if cgen.AVX:
        xmm = "y" + xmm[1:]
        code = "vperm2f128 %s, %s, %s, 0x00 \n" % (xmm, xmm, xmm)
        rounds = n // 8
        for i in range(rounds):
            code += "vmovaps yword[%s + %s + %i], %s\n"  % (reg, path, offset, xmm)
            offset += 32
    else:
        rounds = n // 4
        code = ''
        for i in range(rounds):
            code += "movaps oword[%s + %s + %i], %s\n"  % (reg, path, offset, xmm)
            offset += 16 
    return code

def _spectrum(cgen, args):
    cgen.clear_regs()
    arg = cgen.create_tmp_spec()
    code1, reg1, typ1 = arg.load_cmd(cgen)
    if len(args) == 0:
        return code1, reg1, typ1
    if len(args) == 1:
        code2, xmm, typ2 = load_operand(cgen, args[0])
        if typ2 != Float:
            raise ValueError("Only float for now in first argument of spectrum.")
        if cgen.AVX:
            code3 = "vshufps %s, %s, %s, 0x00\n" % (xmm, xmm, xmm)
        else:
            code3 = "shufps %s, %s, 0x00\n" % (xmm, xmm)
        path = "Spectrum.values"
        if isinstance(arg, RGBSpec):
            code4 = Vec4.store_attr(cgen, path, reg1, xmm)
        else:
            code4 = _set_sampled_spec(cgen, reg1, xmm)
        code = code1 + code2 + code3 + code4
        return code, reg1, typ1

    raise ValueError("Spectrum built in-- wrong number of arguments!")


register_function('spectrum', _spectrum, inline=False) 

def _label_sufix(AVX=False, BIT64=False):
    avx = 'avx' if AVX else 'sse'
    bit = '64' if BIT64 else '32' 
    suffix = '%s_%s' % (avx, bit)
    return suffix

def _math_atanr2_pow(cgen, args, fun_ss, fun_ps):
    if len(args) != 2:
        msg = "Wrong number of arguments in %s, %s fucntion" % (fun_ss, fun_ps)
        raise ValueError(msg, args)

    cgen.clear_regs()
    xmm1 = cgen.register(reg='xmm0')
    xmm2 = cgen.register(reg='xmm1')
    code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=xmm1)
    code2, reg2, typ2 = load_operand(cgen, args[1], dest_reg=xmm2)

    if typ1 != typ2:
        raise ValueError("Type mismatch atanr2 function!", typ1, typ2)

    if typ1 == Float:
        label = fun_ss + '_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_yxa8mm3epu'
        cgen.add_asm_function(fun_ss, label)
    elif typ1 == Vec2 or typ1 == Vec3 or typ1 == Vec4:
        label = fun_ps + '_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_pxp3axmuj'
        cgen.add_asm_function(fun_ps, label)
    else:
        raise ValueError("Unsuported type for math function", typ1)

    code3 = 'call %s\n' % label
    code4 = code1 + code2 + code3
    cgen.release_reg(reg2)
    return code4, 'xmm0', typ1

def _pow(cgen, args):
    return _math_atanr2_pow(cgen, args, 'pow_ss', 'pow_ps')

register_function('pow', _pow, inline=False) 

def _math_fun(cgen, args, fun_ss, fun_ps):
    if len(args) != 1:
        msg = "Wrong number of arguments in %s, %s fucntion" % (fun_ss, fun_ps)
        raise ValueError(msg, args)

    cgen.clear_regs()
    xmm1 = cgen.register(reg='xmm0')
    code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=xmm1)

    if typ1 == Float:
        label = fun_ss + '_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_yxa8mm3epu'
        cgen.add_asm_function(fun_ss, label)
    elif typ1 == Vec2 or typ1 == Vec3 or typ1 == Vec4:
        label = fun_ps + '_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_pxp3axmuj'
        cgen.add_asm_function(fun_ps, label)
    else:
        raise ValueError("Unsuported type for math function", typ1)
    code2 = 'call %s\n' % label
    code3 = code1 + code2
    return code3, 'xmm0', typ1

def _log(cgen, args):
    #TODO log_ss has bug in assembler, probably some instruction is wrong encoded
    # test movd instruction!!!
    return _math_fun(cgen, args, 'log_ps', 'log_ps')

register_function('log', _log, inline=False) 

def _exp(cgen, args):
    return _math_fun(cgen, args, 'exp_ss', 'exp_ps')

register_function('exp', _exp, inline=False)

def _sin(cgen, args):
    return _math_fun(cgen, args, 'sin_ss', 'sin_ps')

register_function('sin', _sin, inline=False)

def _cos(cgen, args):
    return _math_fun(cgen, args, 'cos_ss', 'cos_ps')

register_function('cos', _cos, inline=False)

def _acos(cgen, args):
    return _math_fun(cgen, args, 'acos_ps', 'acos_ps')

register_function('acos', _acos, inline=False)

def _asin(cgen, args):
    return _math_fun(cgen, args, 'asin_ss', 'asin_ps')

register_function('asin', _asin, inline=False)

def _tan(cgen, args):
    return _math_fun(cgen, args, 'tan_ss', 'tan_ps')

register_function('tan', _tan, inline=False)

def _atan(cgen, args):
    return _math_fun(cgen, args, 'atan_ss', 'atan_ps')

register_function('atan', _atan, inline=False)

def _atanr2(cgen, args):
    return _math_atanr2_pow(cgen, args, 'atanr2_ss', 'atanr2_ps')

register_function('atanr2', _atanr2, inline=False)

def _random_funcs(cgen, args, rnd_fun, ret_type):
    if len(args) != 0:
        raise ValueError("Wrong number of arguments in random fucntion", args)
    label = 'random_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_yxa8mm3epu'
    cgen.add_asm_function('random', label)
    code = 'call %s\n' % label
    return code, 'xmm0', ret_type

def _random(cgen, args):
    return _random_funcs(cgen, args, 'random', Float)
register_function('random', _random, inline=False) 

def _random2(cgen, args):
    return _random_funcs(cgen, args, 'random2', Vec2)
register_function('random2', _random2, inline=False) 

def _random3(cgen, args):
    return _random_funcs(cgen, args, 'random3', Vec3)
register_function('random3', _random3, inline=False) 

def _random4(cgen, args):
    return _random_funcs(cgen, args, 'random4', Vec4)
register_function('random4', _random4, inline=False) 

def _sample_hemisphere(cgen, args):
    if len(args) != 0:
        raise ValueError("Wrong number of arguments in sample hemisphere fucntion", args)
    label = 'sample_hemisphere_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_yxa8mm3epu'
    cgen.add_asm_function('sample_hemisphere', label)
    code = 'call %s\n' % label
    return code, 'xmm0', Vec3

register_function('sample_hemisphere', _sample_hemisphere, inline=False)

def _cross_function(cgen, args):
    if len(args) != 2:
        raise ValueError("Wrong number of arguments in dot fucntion", args)
    code1, xmm1, typ1 = load_operand(cgen, args[0])
    code2, xmm2, typ2 = load_operand(cgen, args[1])
    if typ1 != Vec3 or typ2 != Vec3:
        raise ValueError("Two Vec3 argument is expected to cross function", args)

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
    return code, xmm1, Vec3

register_function('cross', _cross_function, inline=True)

def _min_max(cgen, args, inst='max'):
    if len(args) != 2:
        raise ValueError("Wrong number of arguments in min max fucntion", args)
    code1, xmm1, typ1 = load_operand(cgen, args[0])
    code2, xmm2, typ2 = load_operand(cgen, args[1])

    if typ1 != typ2:
        raise ValueError("Arguments must be of the same type in min max function!",
                typ1, typ2)

    if typ1 == Float:
        if cgen.AVX:
            l1 = 'v%sss %s, %s, %s\n' % (inst, xmm1, xmm1, xmm2)
        else:
            l1 = '%sss %s, %s\n' % (inst, xmm1, xmm2)
    elif typ1 == Vec2 or typ1 == Vec3 or typ1 == Vec4:
        if cgen.AVX:
            l1 = 'v%sps %s, %s, %s\n' % (inst, xmm1, xmm1, xmm2)
        else:
            l1 = '%sps %s, %s\n' % (inst, xmm1, xmm2)
    else:
        raise ValueError("Unsuported type of argument in min max function!", typ1)

    cgen.release_reg(xmm2)

    code = code1 + code2 + l1
    return code, xmm1, typ1

def _max(cgen, args):
    return _min_max(cgen, args, 'max')

register_function('max', _max, inline=True)

def _min(cgen, args):
    return _min_max(cgen, args, 'min')

register_function('min', _min, inline=True)

def _sqrt(cgen, args):
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in sqrt fucntion", args)

    code1, xmm1, typ1 = load_operand(cgen, args[0])

    #TODO --- typ1 == Integer
    if typ1 == Float:
        if cgen.AVX:
            l1 = 'vsqrtss %s, %s, %s\n' % (xmm1, xmm1, xmm1)
        else:
            l1 = 'sqrtss %s, %s\n' % (xmm1, xmm1)
    elif typ1 == Vec2 or typ1 == Vec3 or typ1 == Vec4:
        if cgen.AVX:
            l1 = 'vsqrtps %s, %s, %s\n' % (xmm1, xmm1, xmm1)
        else:
            l1 = 'sqrtps %s, %s\n' % (xmm1, xmm1)
    else:
        raise ValueError("Unsuported type of argument in min max function!", typ1)

    code = code1 + l1
    return code, xmm1, typ1

register_function('sqrt', _sqrt, inline=True)


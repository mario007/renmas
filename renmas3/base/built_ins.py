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

    cgen.add_color_func('spectrum_to_rgb')

    code = code1 + "call spectrum_to_rgb\n"
    return code, 'xmm0', Vec3


register_function('spectrum_to_rgb', _spectrum_to_rgb, inline=False) 

def _luminance(cgen, args):
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in normalize fucntion", args)

    cgen.clear_regs()

    s_arg = cgen.get_arg(args[0])
    if isinstance(s_arg, RGBSpec) or isinstance(s_arg, SampledSpec):
        if cgen.BIT64:
            reg1 = cgen.register(typ='general', bit=64, reg='rax')
        else:
            reg1 = cgen.register(typ='general', bit=32, reg='eax')
        code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=reg1)
        cgen.add_color_func('luminance')
        code = code1 + "call luminance\n"
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

    xmm_reg = cgen.register(typ='xmm')
    if cgen.AVX:
        code9 = "vmovaps %s, oword [%s]\n" % (xmm_reg, reg4)
    else:
        code9 = "movaps %s, oword [%s]\n" % (xmm_reg, reg4)

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

def _pow(cgen, args):
    if len(args) != 2:
        raise ValueError("Wrong number of arguments in pow fucntion", args)

    #NOTE here we dont use load_func_args function because pow can accept
    # different type parameters Float, Vector3, ...
    cgen.clear_regs()
    xmm1 = cgen.register(reg='xmm0')
    xmm2 = cgen.register(reg='xmm1')
    code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=xmm1)
    code2, reg2, typ2 = load_operand(cgen, args[1], dest_reg=xmm2)

    if typ1 != typ2:
        raise ValueError("Type mismatch", typ1, typ2)

    if typ1 == Float:
        label = 'fast_pow_ss_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_yxa8mm3epu'
        cgen.add_asm_function('pow_ss', label)
    elif typ1 == Vec2 or typ1 == Vec3 or typ1 == Vec4:
        label = 'fast_pow_ps_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_pxp3axmuj'
        cgen.add_asm_function('pow_ps', label)
    else:
        raise ValueError("Unsuported type for pow", typ1)
    code3 = 'call %s\n' % label
    code3 = code1 + code2 + code3
    return code3, 'xmm0', typ1

register_function('pow', _pow, inline=False) 

def _log(cgen, args):
    if len(args) != 1:
        raise ValueError("Wrong number of arguments in pow fucntion", args)

    #NOTE here we dont use load_func_args function because pow can accept
    # different type parameters Float, Vector3, ...
    cgen.clear_regs()
    xmm1 = cgen.register(reg='xmm0')
    code1, reg1, typ1 = load_operand(cgen, args[0], dest_reg=xmm1)

    if typ1 == Float:
        label = 'fast_log_ss_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_yxa8mm3epu'
        cgen.add_asm_function('log_ss', label)
    elif typ1 == Vec2 or typ1 == Vec3 or typ1 == Vec4:
        label = 'fast_log_ps_' + _label_sufix(cgen.AVX, cgen.BIT64) + '_pxp3axmuj'
        cgen.add_asm_function('log_ps', label)
    else:
        raise ValueError("Unsuported type for pow", typ1)
    code2 = 'call %s\n' % label
    code3 = code1 + code2
    return code3, 'xmm0', typ1

register_function('log', _log, inline=False) 


import platform
import renmas3.switch as proc

from .arg import Integer, Float, Vec3, Struct, Attribute

from .instr import load_struct_ptr
from .instr import load_int_into_reg, load_float_into_reg, load_vec3_into_reg
from .instr import store_int_from_reg, store_float_from_reg, store_vec3_from_reg
from .instr import store_const_into_mem, convert_float_to_int, convert_int_to_float
from .instr import load_operand, store_operand, negate_operand

from .cgen import register_function

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
        code += convert_float_to_int(reg, to_reg)
        cgen.release_reg(reg)
        return code, to_reg, Integer
    else:
        raise ValueError("Unsuported argument type", args[0])

register_function('int', _int_function, inline=True) 

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
        line3 = "vdivps %s, %s\n" % (reg1, tmp1)
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
        line4 = "addps %s, %s\n" % (tmp2, tmp1)
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

def _get_rgb(cgen, args):
    if len(args) != 3:
        raise ValueError("Wrong number of arguments in get_rgb fucntion", args)
    arg1 = cgen.get_arg(args[0])
    if arg1.typ.typ != "ImageFloatRGBA":
        raise ValueError("Wrong image format", arg1.typ.typ)
    code1, reg1, typ1 = load_operand(cgen, args[1])
    code2, reg2, typ2 = load_operand(cgen, args[2])
    if typ1 != Integer or typ2 != Integer:
        raise ValueError("Argument for x and y must be integers", typ1, typ2)

    src = Attribute(arg1.name, 'pitch')
    reg3 = cgen.register(typ='general')
    code3 = load_int_into_reg(cgen, reg3, src)
    code4 = "imul %s, %s\n" % (reg2, reg3)
    code5 = "imul %s, %s, 16\n" % (reg1, reg1) 
    code6 = "add %s, %s\n" % (reg2, reg1)

    cgen.release_reg(reg1)
    cgen.release_reg(reg3)

    code7, reg4, path = load_struct_ptr(cgen, Attribute(arg1.name, 'pixels_ptr'))

    bits = platform.architecture()[0]
    if bits == '64bit':
        reg5 = cgen.register(typ='general', bit=64)
        code8 = "mov %s, qword [%s + %s]\n" % (reg5, reg4, path)
        code9 = "add %s, %s\n" % (reg5, 'r' + reg2[1:]) #TODO better handle conversion of 32 and 64 registers
    else:
        reg5 = cgen.register(typ='general', bit=32)
        code8 = "mov %s, dword [%s + %s]\n" % (reg5, reg4, path)
        code9 = "add %s, %s\n" % (reg5, reg2)

    xmm_reg = cgen.register(typ='xmm')
    if proc.AVX:
        code10 = "vmovaps %s, oword [%s]\n" % (xmm_reg, reg5)
    else:
        code10 = "movaps %s, oword [%s]\n" % (xmm_reg, reg5)

    cgen.release_reg(reg2)
    cgen.release_reg(reg4)
    cgen.release_reg(reg5)

    code = code1 + code2 + code3 + code4 + code5 + code6 + code7 + code8 + code9 + code10
    return code, xmm_reg, Vec3

register_function('get_rgb', _get_rgb, inline=True) 

def _set_rgb(cgen, args):
    if len(args) != 4:
        raise ValueError("Wrong number of arguments in get_rgb fucntion", args)
    arg1 = cgen.get_arg(args[0])
    if arg1.typ.typ != "ImageFloatRGBA":
        raise ValueError("Wrong image format", arg1.typ.typ)
    code1, reg1, typ1 = load_operand(cgen, args[1])
    code2, reg2, typ2 = load_operand(cgen, args[2])
    if typ1 != Integer or typ2 != Integer:
        raise ValueError("Argument for x and y must be integers", typ1, typ2)

    src = Attribute(arg1.name, 'pitch')
    reg3 = cgen.register(typ='general')
    code3 = load_int_into_reg(cgen, reg3, src)
    code4 = "imul %s, %s\n" % (reg2, reg3)
    code5 = "imul %s, %s, 16\n" % (reg1, reg1) 
    code6 = "add %s, %s\n" % (reg2, reg1)

    cgen.release_reg(reg1)
    cgen.release_reg(reg3)

    code7, reg4, path = load_struct_ptr(cgen, Attribute(arg1.name, 'pixels_ptr'))

    bits = platform.architecture()[0]
    if bits == '64bit':
        reg5 = cgen.register(typ='general', bit=64)
        code8 = "mov %s, qword [%s + %s]\n" % (reg5, reg4, path)
        code9 = "add %s, %s\n" % (reg5, 'r' + reg2[1:]) #TODO better handle conversion of 32 and 64 registers
    else:
        reg5 = cgen.register(typ='general', bit=32)
        code8 = "mov %s, dword [%s + %s]\n" % (reg5, reg4, path)
        code9 = "add %s, %s\n" % (reg5, reg2)

    code10, xmm_reg, typ3 = load_operand(cgen, args[3])
    if typ3 != Vec3:
        raise ValueError("Operand is expected to be Vec3 type", typ3)

    if proc.AVX:
        code11 = "vmovaps oword [%s], %s\n" % (reg5, xmm_reg)
    else:
        code11 = "movaps oword [%s], %s\n" % (reg5, xmm_reg)

    cgen.release_reg(reg2)
    cgen.release_reg(reg4)
    cgen.release_reg(reg5)
    cgen.release_reg(xmm_reg)

    code = code1 + code2 + code3 + code4 + code5 + code6 + code7 + code8 + code9 + code10 + code11
    return code, reg1, Integer

register_function('set_rgb', _set_rgb, inline=True) 

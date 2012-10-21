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


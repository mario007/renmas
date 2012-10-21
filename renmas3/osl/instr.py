import struct
import platform
from .arg import  Integer, Float, Vec3, Struct, Attribute, StructPtr

def valid_reg32(reg):
    fs = frozenset(['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax'])
    if reg not in fs:
        raise ValueError("Register mismatch 32-bit register is expected", reg)

def valid_reg64(reg):
    fs = frozenset(['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax'])
    if reg not in fs:
        raise ValueError("Register mismatch 64-bit register is expected", reg)

def load_struct_ptr(cgen, attr, reg=None):
    bits = platform.architecture()[0]
    if isinstance(attr, str):
        name = attr
        path = None
    else:
        name = attr.name
        path = attr.path

    arg = cgen.get_arg(name) # arg is Struct
    if not isinstance(arg, Struct) and not isinstance(arg, StructPtr):
        raise ValueError("Struct or StructPtr is expected and not ", arg)
    if bits == '64bit':
        reg = cgen.register(typ='general', bit=64) if reg is None else reg
        valid_reg64(reg)
        if isinstance(arg, StructPtr):
            code = "mov %s, qword [%s] \n" % (reg, name)
        else:
            code = "mov %s, %s \n" % (reg, name)
    else:
        reg = cgen.register(typ='general', bit=32) if reg is None else reg
        valid_reg32(reg)
        if isinstance(arg, StructPtr):
            code = "mov %s, dword [%s] \n" % (reg, name)
        else:
            code = "mov %s, %s \n" % (reg, name)
    
    if path is not None:
        path = arg.typ.typ + "." + path
    return (code, reg, path)

def load_int_into_reg(cgen, reg, src, op_reg=None):
    if isinstance(src, str):
        code = "mov %s, dword [%s] \n" % (reg, src)
    elif isinstance(src, int):
        code = "mov %s, %i \n" % (reg, src)
    elif isinstance(src, Attribute):
        code, reg2, path = load_struct_ptr(cgen, src, op_reg)
        code += "mov %s, dword [%s + %s]\n" % (reg, reg2, path)
        cgen.release_reg(reg2)
    else:
        raise ValueError("Unknown source of int", src)
    return code

def store_int_from_reg(cgen, reg, dest, op_reg=None):
    if isinstance(dest, str):
        code = "mov dword [%s], %s \n" % (dest, reg)
    elif isinstance(dest, Attribute):
        code, reg2, path = load_struct_ptr(cgen, dest, op_reg)
        code += "mov dword [%s + %s], %s\n" % (reg2, path, reg)
        cgen.release_reg(reg2)
    else:
        raise ValueError("Unknown destination", dest)
    return code
    
def load_float_into_reg(cgen, reg, src, op_reg=None): #reg must be xmm
    if isinstance(src, str):
        code = "movss %s, dword [%s] \n" % (reg, src)
    elif isinstance(src, float):
        #TODO create const in cgen
        raise ValueError("Not implemented yet")
    elif isinstance(src, Attribute):
        code, reg2, path = load_struct_ptr(cgen, src, op_reg)
        code += "movss %s, dword [%s + %s]\n" % (reg, reg2, path)
        cgen.release_reg(reg2)
    else:
        raise ValueError("Unknown source", src)
    return code

def store_float_from_reg(cgen, reg, dest, op_reg=None):
    if isinstance(dest, str):
        code = "movss dword [%s], %s \n" % (dest, reg)
    elif isinstance(dest, Attribute):
        code, reg2, path = load_struct_ptr(cgen, dest, op_reg)
        code += "movss dword [%s + %s], %s\n" % (reg2, path, reg)
        cgen.release_reg(reg2)
    else:
        raise ValueError("Unknown destination", dest)
    return code

def load_vec3_into_reg(cgen, reg, src, op_reg=None): #reg must be xmm
    if isinstance(src, str):
        code = "movaps %s, oword [%s] \n" % (reg, src)
    elif isinstance(src, Attribute):
        code, reg2, path = load_struct_ptr(cgen, src, op_reg)
        code += "movaps %s, oword [%s + %s]\n" % (reg, reg2, path)
        cgen.release_reg(reg2)
    else:
        raise ValueError("Unknown source", src)
    return code

def store_vec3_from_reg(cgen, reg, dest, op_reg=None):
    if isinstance(dest, str):
        code = "movaps oword [%s], %s \n" % (dest, reg)
    elif isinstance(dest, Attribute):
        code, reg2, path = load_struct_ptr(cgen, dest, op_reg)
        code += "movaps oword [%s + %s], %s\n" % (reg2, path, reg)
        cgen.release_reg(reg2)
    else:
        raise ValueError("Unknown destination")
    return code

def convert_int_to_float(reg, to_reg):
    return "cvtsi2ss %s, %s \n" % (to_reg, reg)

def convert_float_to_int(reg, to_reg):
    return "cvttss2si %s, %s \n" % (to_reg, reg)

def float2hex(f):
    r = struct.pack('f', f)
    r1 = struct.unpack('I', r)[0]
    return hex(r1)

def store_const_into_mem(cgen, dest, const, offset=None):
    if isinstance(dest, Attribute):
        code, reg, path = load_struct_ptr(cgen, dest)
        if isinstance(const, float):
            fl = float2hex(const)
            if offset is not None:
                code += "mov dword [%s + %s + %i], %s ;float value = %f \n" % (reg, path, offset, fl, const)
            else:
                code += "mov dword [%s + %s], %s ;float value = %f \n" % (reg, path, fl, const)
        elif isinstance(const, int):
            if offset is not None:
                code += "mov dword [%s + %s + %i], %i\n" % (reg, path, offset, const)
            else:
                code += "mov dword [%s + %s], %i\n" % (reg, path, const)
        else:
            raise ValueError("Unsuported constant")

    elif isinstance(dest, str):
        if isinstance(const, float):
            fl = float2hex(const)
            code = 'mov dword [%s], %s ;float value = %f \n' % (dest, fl, const)
            if offset is not None:
                code = 'mov dword [%s + %i], %s ;float value = %f \n' % (dest, offset, fl, const)
        elif isinstance(const, int):
            code = 'mov dword [%s], %i \n' % (dest, const)
            if offset is not None:
                code = 'mov dword [%s + %i], %i \n' % (dest, offset, const)
        else:
            raise ValueError("Unsuported constant", const)
    else:
        raise ValueError("Unknown destination")
    return code

def load_argument(cgen, arg, op):
    if isinstance(arg, Integer):
        reg = cgen.register(typ='general')
        code = load_int_into_reg(cgen, reg, op)
        typ = Integer
    elif isinstance(arg, Float):
        reg = cgen.register(typ='xmm')
        code = load_float_into_reg(cgen, reg, op)
        typ = Float
    elif isinstance(arg, Vec3):
        reg = cgen.register(typ='xmm')
        code = load_vec3_into_reg(cgen, reg, op)
        typ = Vec3
    else:
        raise ValueError("Unknown argument", arg)
    return (code, reg, typ)

def load_operand(cgen, op):
    if isinstance(op, int):
        reg = cgen.register(typ='general')
        code = "mov %s, %i\n" % (reg, op)
        typ = Integer 
    elif isinstance(op, float):
        con_arg = cgen.create_const(op)
        reg = cgen.register(typ='xmm')
        code = load_float_into_reg(cgen, reg, con_arg.name)
        typ = Float
    elif isinstance(op, str) or isinstance(op, Attribute):
        arg = cgen.get_arg(op)
        if arg is None:
            raise ValueError("Operand doesn't exist", op)
        code, reg, typ = load_argument(cgen, arg, op)
    else:
        raise ValueError("Unknown operand")
    return (code, reg, typ)

def store_operand(cgen, dest, reg, typ):
    dst_arg = cgen.create_arg(dest, typ=typ)

    if isinstance(dst_arg, Integer) and typ == Integer:
        code = store_int_from_reg(cgen, reg, dest)
    elif isinstance(dst_arg, Float) and typ == Float:
        code = store_float_from_reg(cgen, reg, dest)
    elif isinstance(dst_arg, Float) and typ == Integer:
        to_reg = cgen.register(typ='xmm')
        code = convert_int_to_float(reg, to_reg)
        code += store_float_from_reg(cgen, to_reg, dest)
    elif isinstance(dst_arg, Vec3) and typ == Vec3:
        code = store_vec3_from_reg(cgen, reg, dest)
    else:
        raise ValueError("Unsuported operand", reg, typ, dest)
    return code

def negate_operand(cgen, unary, reg, typ):
    code = ''
    if unary is not None and unary == '-':
        if typ == Integer:
            reg2 = cgen.register(typ='general')
            line1 = "xor %s, %s\n" % (reg2, reg2)
            line2 = "sub %s, %s\n" % (reg2, reg)
            code = line1 + line2
            return (code, reg2)
        elif typ == Float:
            arg = cgen.create_const((-1.0, -1.0, -1.0))
            code = "mulss %s, dword[%s]\n" % (reg, arg.name) 
            return (code, reg)
        elif typ == Vec3:
            arg = cgen.create_const((-1.0, -1.0, -1.0))
            code = "mulps %s, oword[%s]\n" % (reg, arg.name) 
            return (code, reg)
        else:
            raise ValueError("Unsuported operand type", typ)
    return (code, reg)


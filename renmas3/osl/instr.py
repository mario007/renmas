import struct
import platform
from .arg import  IntArg, FloatArg, Vector3Arg, StructArg, Attribute

def valid_reg32(reg):
    return True

def valid_reg64(reg):
    return True

def load_struct_ptr(cgen, attr, reg=None):
    bits = platform.architecture()[0]
    arg = cgen.get_arg(attr.name) # arg is StructArg
    if not isinstance(arg, StructArg):
        raise ValueError("StructArg is expected and not ", arg)
    if bits == '64bit':
        reg = cgen.register(typ='general', bit=64) if reg is None else reg
        valid_reg64(reg)
        if cgen.is_input_arg(arg):
            code = "mov %s, qword [%s] \n" % (reg, attr.name)
        else:
            code = "mov %s, %s \n" % (reg, attr.name)
    else:
        reg = cgen.register(typ='general', bit=32) if reg is None else reg
        valid_reg32(reg)
        if cgen.is_input_arg(arg):
            code = "mov %s, dword [%s] \n" % (reg, attr.name)
        else:
            code = "mov %s, %s \n" % (reg, attr.name)
    
    path = None
    if attr.path is not None:
        path = arg.typ.typ + "." + attr.path
    return (code, reg, path)

def load_int_into_reg(cgen, reg, src, op_reg=None):
    if isinstance(src, str):
        code = "mov %s, dword [%s] \n" % (reg, src)
    elif isinstance(src, int):
        code = "mov %s, %i \n" % (reg, src)
    elif isinstance(src, Attribute):
        code, reg2, path = load_struct_ptr(cgen, src, op_reg)
        code += "mov %s, dword [%s + %s]\n" % (reg, reg2, path)
    else:
        raise ValueError("Unknown source of int", src)
    return code

def store_int_from_reg(cgen, reg, dest, op_reg=None):
    if isinstance(dest, str):
        code = "mov dword [%s], %s \n" % (dest, reg)
    elif isinstance(dest, Attribute):
        code, reg2, path = load_struct_ptr(cgen, dest, op_reg)
        code += "mov dword [%s + %s], %s\n" % (reg2, path, reg)
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
    else:
        raise ValueError("Unknown source", src)
    return code

def store_float_from_reg(cgen, reg, dest, op_reg=None):
    if isinstance(dest, str):
        code = "movss dword [%s], %s \n" % (dest, reg)
    elif isinstance(dest, Attribute):
        code, reg2, path = load_struct_ptr(cgen, dest, op_reg)
        code += "movss dword [%s + %s], %s\n" % (reg2, path, reg)
    else:
        raise ValueError("Unknown destination", dest)
    return code

def load_vec3_into_reg(cgen, reg, src, op_reg=None): #reg must be xmm
    if isinstance(src, str):
        code = "movaps %s, oword [%s] \n" % (reg, src)
    elif isinstance(src, Attribute):
        code, reg2, path = load_struct_ptr(cgen, src, op_reg)
        code += "movaps %s, oword [%s + %s]\n" % (reg, reg2, path)
    else:
        raise ValueError("Unknown source", src)
    return code

def store_vec3_from_reg(cgen, reg, dest, op_reg=None):
    if isinstance(dest, str):
        code = "movaps oword [%s], %s \n" % (dest, reg)
    elif isinstance(dest, Attribute):
        code, reg2, path = load_struct_ptr(cgen, dest, op_reg)
        code += "movaps oword [%s + %s], %s\n" % (reg2, path, reg)
    else:
        raise ValueError("Unknown destination")
    return code

def copy_int_to_int(cgen, dest, src):
    reg = cgen.register(typ='general')
    code = load_int_into_reg(cgen, reg, src)
    code += store_int_from_reg(cgen, reg, dest)
    return code

def copy_float_to_float(cgen, dest, src):
    reg = cgen.register(typ='xmm')
    code = load_float_into_reg(cgen, reg, src)
    code += store_float_from_reg(cgen, reg, dest)
    return code

def copy_vec3_to_vec3(cgen, dest, src):
    reg = cgen.register(typ='xmm')
    code = load_vec3_into_reg(cgen, reg, src)
    code += store_vec3_from_reg(cgen, reg, dest)
    return code

def convert_int_to_float(reg, to_reg):
    return "cvtsi2ss %s, %s \n" % (to_reg, reg)

def convert_float_to_int(reg, to_reg):
    return "cvttss2si %s, %s \n" % (to_reg, reg)

def copy_int_to_float(cgen, dest, src):
    reg = cgen.register(typ='general')
    to_reg = cgen.register(typ='xmm')
    code = load_int_into_reg(cgen, reg, src)
    code += convert_int_to_float(reg, to_reg)
    code += store_float_from_reg(cgen, to_reg, dest)
    return code

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


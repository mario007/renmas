import platform
import renmas3.switch as proc
from .arg import  Integer, Float, Vec3, Struct, Attribute, StructPtr, Const, Name, Subscript
from .util import float2hex

def load_struct_ptr(cgen, attr, reg=None):
    bits = platform.architecture()[0]
    if isinstance(attr, Name):
        name = attr.name
        path = None
    elif isinstance(attr, Attribute):
        name = attr.name
        path = attr.path
    else:
        raise ValueError("Unsuported operand type for loading struct pointer.", attr)

    arg = cgen.get_arg(name) # arg is Struct
    if not isinstance(arg, Struct) and not isinstance(arg, StructPtr):
        raise ValueError("Struct or StructPtr is expected and not ", arg)
    if bits == '64bit':
        reg = cgen.register(typ='general', bit=64) if reg is None else reg
        if not cgen.regs.is_reg64(reg):
            raise ValueError("64-bit general register is expected!", reg)
        if isinstance(arg, StructPtr):
            code = "mov %s, qword [%s] \n" % (reg, name)
        else:
            code = "mov %s, %s \n" % (reg, name)
    else:
        reg = cgen.register(typ='general', bit=32) if reg is None else reg
        if not cgen.regs.is_reg32(reg):
            raise ValueError("32-bit general register is expected!", reg)
        if isinstance(arg, StructPtr):
            code = "mov %s, dword [%s] \n" % (reg, name)
        else:
            code = "mov %s, %s \n" % (reg, name)
    
    if path is not None:
        path = arg.typ.typ + "." + path
    return (code, reg, path)

def convert_int_to_float(reg, xmm):
    return "cvtsi2ss %s, %s \n" % (xmm, reg)

def convert_float_to_int(reg, to_reg):
    return "cvttss2si %s, %s \n" % (to_reg, reg)

def store_const_into_mem(cgen, dest, const, offset=None):
    #TODO -- be careful to binding to differenent argument
    # we cant directly write dest, we must create argument
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

    elif isinstance(dest, Name):
        if isinstance(const, float):
            fl = float2hex(const)
            code = 'mov dword [%s], %s ;float value = %f \n' % (dest.name, fl, const)
            if offset is not None:
                code = 'mov dword [%s + %i], %s ;float value = %f \n' % (dest.name, offset, fl, const)
        elif isinstance(const, int):
            code = 'mov dword [%s], %i \n' % (dest.name, const)
            if offset is not None:
                code = 'mov dword [%s + %i], %i \n' % (dest.name, offset, const)
        else:
            raise ValueError("Unsuported constant", const)
    else:
        raise ValueError("Unknown destination", dest)
    return code

def load_const(cgen, const, dest_reg=None):
    if isinstance(const, int):
        if dest_reg is not None and cgen.regs.is_xmm(dest_reg):
            tmp = cgen.register(typ='general')
            code = "mov %s, %i\n" % (tmp, const)
            conversion = convert_int_to_float(tmp, dest_reg)
            cgen.release_reg(tmp)
            return code + conversion, dest_reg, Float

        if dest_reg is None:
            dest_reg = cgen.register(typ='general')
        code = "mov %s, %i\n" % (dest_reg, const)
        return code, dest_reg, Integer
    elif isinstance(const, float):
        if dest_reg is None:
            dest_reg = cgen.register(typ='xmm')
        arg = cgen.create_const(const)
        if proc.AVX:
            code = "vmovss %s, dword [%s] \n" % (dest_reg, arg.name)
        else:
            code = "movss %s, dword [%s] \n" % (dest_reg, arg.name)
        return code, dest_reg, Float 
    else:
        raise ValueError("Not yet suported constant", const)

def load_subscript(cgen, op, dest_reg=None, ptr_reg=None):
    raise ValueError("Not yet implemented loading of subscript")

def load_operand(cgen, op, dest_reg=None, ptr_reg=None):
    if isinstance(op, Const):
        return load_const(cgen, op.const, dest_reg)
    elif isinstance(op, Name) or isinstance(op, Attribute):
        arg = cgen.get_arg(op)
        if arg is None:
            raise ValueError("Argument doesn't exist", op)
        if isinstance(op, Name):
            return arg.load_cmd(cgen, arg.name, dest_reg)
        else:
            code, ptr_reg2, path = load_struct_ptr(cgen, op, ptr_reg)
            code2, dest_reg, typ =  arg.load_cmd(cgen, arg.name, dest_reg, path=path, ptr_reg=ptr_reg2)
            if ptr_reg is None:
                cgen.release_reg(ptr_reg2)
            return code + code2, dest_reg, typ
    elif isinstance(op, Subscript):
        return load_subscript(cgen, op, dest_reg, ptr_reg)
    else:
        raise ValueError("Unsuported operand type", op)

def store_operand(cgen, dest, reg, typ):
    dst_arg = cgen.create_arg(dest, typ=typ)

    code = ''
    #implicit conversion int to float
    if isinstance(dst_arg, Float) and typ == Integer:
        to_reg = cgen.register(typ='xmm')
        code = convert_int_to_float(reg, to_reg)
        reg = to_reg
        typ = Float

    if type(dst_arg) != typ:
        raise ValueError("Type mismatch, cannot sotre operand", type(dst_arg), typ)

    if isinstance(dest, Name):
        code += dst_arg.store_cmd(cgen, reg, dest.name)
    elif isinstance(dest, Attribute):
        code2, ptr_reg, path = load_struct_ptr(cgen, dest)
        code += code2
        code += dst_arg.store_cmd(cgen, reg, dest.name, path=path, ptr_reg=ptr_reg)
        cgen.release_reg(ptr_reg)
    else:
        raise ValueError("Unknown type of destination.", dest)
    return code


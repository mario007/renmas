import platform
import renmas3.switch as proc
from .arg import  Integer, Float, Vec3, Struct, Attribute, StructPtr, Const, Name, Subscript
from .arg import conv_int_to_float
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
            code = "mov %s, qword [%s] \n" % (reg, arg.name)
        else:
            code = "mov %s, %s \n" % (reg, arg.name)
    else:
        reg = cgen.register(typ='general', bit=32) if reg is None else reg
        if not cgen.regs.is_reg32(reg):
            raise ValueError("32-bit general register is expected!", reg)
        if isinstance(arg, StructPtr):
            code = "mov %s, dword [%s] \n" % (reg, arg.name)
        else:
            code = "mov %s, %s \n" % (reg, arg.name)
    
    if path is not None:
        path = arg.typ.typ + "." + path
    return (code, reg, path)

def extract_index(index):
    if not isinstance(index, Const):
        raise ValueError("Only constant index for now!")
    if not isinstance(index.const, int):
        raise ValueError("Index must be integer constant!")
    return index.const

def load_operand(cgen, op, dest_reg=None, ptr_reg=None):
    if isinstance(op, Const):
        arg = cgen.create_const(op.const)
        return arg.load_cmd(cgen, dest_reg)
    if not isinstance(op, (Name, Attribute, Subscript)):
        raise ValueError("Can't load operand of type ", op)
    arg = cgen.get_arg(op.name)
    if arg is None:
        raise ValueError("Argument doesn't exist", op.name)
    if isinstance(op, Name):
        return arg.load_cmd(cgen, dest_reg)
    elif isinstance(op, Attribute) and isinstance(arg, Struct):
        return arg.load_attr_cmd(cgen, op.path, dest_reg, ptr_reg)
    elif isinstance(op, Subscript):
        if op.path is not None and isinstance(arg, Struct):
            #NOTE this is note yet implemented!!!!!
            return arg.load_subscript(cgen, op.path, op.index, dest_reg, ptr_reg)
        elif op.path is None:
            return arg.load_subscript(cgen, extract_index(op.index), dest_reg)
        else:
            raise ValueError("Can't load operand!", op, arg)
    else:
        raise ValueError("Can't load operand!", op, arg)

def store_operand(cgen, dest, reg, typ):
    dst_arg = cgen.create_arg(dest, typ=typ)
    code = ''

    #implicit conversion int to float
    arg = dst_arg
    if isinstance(dest, Attribute):
        arg = dst_arg.get_argument('%s.%s' % (dest.name, dest.path))
    if isinstance(arg, Float) and typ == Integer:
        to_reg = cgen.register(typ='xmm')
        code = conv_int_to_float(cgen, reg, to_reg)
        reg = to_reg
        typ = Float

    if isinstance(dest, Name):
        if type(dst_arg) != typ:
            raise ValueError("Type mismatch, cannot store operand", type(dst_arg), typ)
        code += dst_arg.store_cmd(cgen, reg)
    elif isinstance(dest, Attribute):
        arg = dst_arg.get_argument('%s.%s' % (dest.name, dest.path))
        if type(arg) != typ:
            raise ValueError("Type mismatch, cannot store operand", type(arg), typ)
        code += dst_arg.store_attr_cmd(cgen, dest.path, reg)
    elif isinstance(dest, Subscript):
        if not arg.item_supported(typ):
            raise ValueError("Argument doesn't support that item type!", arg, typ)
        if dest.path is None:
            code += arg.store_subscript(cgen, reg, typ, extract_index(dest.index))
        else:
            raise ValueError("Subscript attribut is not yet implemented!")
    else:
        raise ValueError("Unknown type of destination.", dest)
    return code

def load_func_args(cgen, operands, in_args):
    if len(operands) != len(in_args):
        raise ValueError("Argument length mismatch", operands, in_args)

    cgen.clear_regs()
    bits = platform.architecture()[0]
    xmm = ['xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['esi', 'edx', 'ecx', 'ebx', 'eax']
    ptr_reg = 'rbp' if bits == '64bit' else 'ebp'
    reg2 = 'edi'
    tmp_xmm = 'xmm7'
    cgen.register(reg=ptr_reg)
    cgen.register(reg=reg2)

    code = ''
    for operand, arg in zip(operands, in_args):
        if type(arg) is Integer:
            reg = general.pop()
            cgen.register(reg=reg)
            co, reg, typ = load_operand(cgen, operand, dest_reg=reg, ptr_reg=ptr_reg)
            code += co
            if typ != Integer:
                raise ValueError("Type mismatch when passing parameter to function", type(arg), typ)
        elif type(arg) is Float or type(arg) is Vec3:
            reg = xmm.pop()
            co, reg, typ = load_operand(cgen, operand, dest_reg=reg, ptr_reg=ptr_reg)
            code += co
            if typ != type(arg):
                raise ValueError("Type mismatch when passing parameter to function", type(arg), typ)
        elif type(arg) is StructPtr:
            reg = general.pop()
            if bits == '64bit':
                reg = 'r' + reg[1:]
            arg2 = cgen.get_arg(operand)
            if isinstance(arg2, Struct):
                if arg.typ.typ != arg2.typ.typ:
                    raise ValueError("Wrong structure type in function argument!", arg.typ.typ, arg2.typ.typ)
                co, dummy, dummy = load_struct_ptr(cgen, operand, reg)
                code += co
            else:
                raise ValueError("User type argument is expected.", arg2)
        else:
            raise ValueError("Unsuported argument type!", operand, type(arg))
    return code

def store_func_args(cgen, args):
    xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    bits = platform.architecture()[0]
    for a in args:
        if isinstance(a, Integer):
            code += "mov dword [%s], %s \n" % (a.name, general.pop())
        elif isinstance(a, Float):
            if cgen.AVX:
                code += "vmovss dword [%s], %s \n" % (a.name, xmm.pop())
            else:
                code += "movss dword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, Vec3):
            if cgen.AVX:
                code += "vmovaps oword [%s], %s \n" % (a.name, xmm.pop())
            else:
                code += "movaps oword [%s], %s \n" % (a.name, xmm.pop())
        elif isinstance(a, StructPtr):
            if bits == '64bit':
                reg = general.pop()
                reg = 'r' + reg[1:]
                code += "mov qword [%s], %s \n" % (a.name, reg)
            else:
                code += "mov dword [%s], %s \n" % (a.name, general.pop())
        else:
            raise ValueError('Unknown argument', a, a.name)
    return code

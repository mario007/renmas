from .arg import Attribute, Const, Name, Subscript, conv_int_to_float
from .integer import Integer, Float
from .usr_type import  Struct, StructPtr
from .spec import RGBSpec, SampledSpec

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
            return arg.load_attr_subscript_cmd(cgen, op.path,
                    extract_index(op.index), dest_reg, ptr_reg)
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
        if dest.path is None:
            code += arg.store_subscript(cgen, reg, typ, extract_index(dest.index))
        else:
            arg = dst_arg.get_argument('%s.%s' % (dest.name, dest.path))
            if not arg.item_supported(typ):
                raise ValueError("Argument doesn't support that item type!", arg, typ)
            code += dst_arg.store_attr_subscript_cmd(cgen, dest.path, reg, typ, extract_index(dest.index))
    else:
        raise ValueError("Unknown type of destination.", dest)
    return code

def load_func_args(cgen, operands, in_args):
    if len(operands) != len(in_args):
        raise ValueError("Argument length mismatch", operands, in_args)

    cgen.clear_regs()
    xmm = ['xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['esi', 'edx', 'ecx', 'ebx', 'eax']
    ptr_reg = 'rbp' if cgen.BIT64 else 'ebp'
    reg2 = 'edi'
    tmp_xmm = 'xmm7'
    cgen.register(reg=ptr_reg)
    cgen.register(reg=reg2)

    code = ''
    #TODO -- test implict conversion from int to float
    for operand, arg in zip(operands, in_args):
        if type(arg) is Struct:
            raise ValueError("StructPtr is expected not Struct as argument!", arg)
        if arg.register_type() == 'pointer':
            reg = general.pop()
            if cgen.BIT64:
                reg = 'r' + reg[1:]
        elif arg.register_type() == 'xmm':
            reg = xmm.pop()
        elif arg.register_type() == 'general':
            reg = general.pop()
        else:
            raise ValueError("Unsuported register type! ", arg.register_type())

        cgen.register(reg=reg)
        co, reg, typ = load_operand(cgen, operand, dest_reg=reg, ptr_reg=ptr_reg)
        code += co
        if not isinstance(arg, typ):
            raise ValueError("Type mismatch when passing parameter to function", type(arg), typ)

        arg2 = cgen.get_arg(operand)
        if isinstance(arg2, Struct):
            if arg.typ.typ != arg2.typ.typ:
                raise ValueError("Wrong structure type in function argument!", arg.typ.typ, arg2.typ.typ)
    return code

def store_func_args(cgen, args):
    #NOTE store_cmd will not work if some allocation of register is needed!!!!
    # be careful and implement better(safe) solution from this problem
    # maybe argument needs extra method stor_cmd_arg?
    xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    for arg in args:
        if arg.register_type() == 'pointer':
            reg = general.pop()
            if cgen.BIT64:
                reg = 'r' + reg[1:]
        elif arg.register_type() == 'xmm':
            reg = xmm.pop()
        elif arg.register_type() == 'general':
            reg = general.pop()
        else:
            raise ValueError("Unsuported register type! ", arg.register_type())
        
        if isinstance(arg, (RGBSpec, SampledSpec)):
            raise ValueError("Spectrum as argument are not yet implemented!")
        code += arg.store_cmd(cgen, reg)
    return code

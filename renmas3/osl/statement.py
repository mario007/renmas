import struct
import platform
from .arg import  IntArg, FloatArg, Vector3Arg, StructArg, Attribute, Function
from .cgen import register_function

from .instr import load_struct_ptr
from .instr import load_int_into_reg, load_float_into_reg, load_vec3_into_reg
from .instr import store_int_from_reg, store_float_from_reg, store_vec3_from_reg
from .instr import copy_int_to_int, copy_float_to_float, copy_vec3_to_vec3, copy_int_to_float
from .instr import store_const_into_mem, convert_float_to_int, convert_int_to_float

def float2hex(f):
    r = struct.pack('f', f)
    r1 = struct.unpack('I', r)[0]
    return hex(r1)

def is_num(obj):
    return isinstance(obj, int) or isinstance(obj, float)

def preform_arithmetic(n1, n2, op):
    if op == '+':
        return n1 + n2 
    elif op == '-':
        return n1 - n2
    elif op == '*':
        return n1 * n2
    elif op == '/':
        return n1 / n2
    elif op == '%':
        return n1 % n2
    else:
        raise ValueError("Unknown operator", op)

def _copy_to_regs(cgen, args, input_args):
    if len(args) != len(input_args):
        raise ValueError("Argument length mismatch", args, input_args)

    xmm = ['xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['esi', 'edx', 'ecx', 'ebx', 'eax']
    ptr_reg = 'ebp'
    ptr_reg2 = 'edi'
    tmp_xmm = 'xmm7'
    bits = platform.architecture()[0]

    code = ''
    for arg1, arg2 in zip(args, input_args):
        if isinstance(arg1, int):
            if type(arg2) == IntArg:
                reg = general.pop()
                code += "mov %s, %i\n" % (reg, arg1)
            elif type(arg2) == FloatArg:
                raise ValueError("Konverzija float konstante-temp variabla?")
            else:
                raise ValueError("Type mismatch", arg1, arg2)
        elif isinstance(arg1, float):
            raise ValueError("Float argument-temp const variable?", arg1)
        elif isinstance(arg1, str) or isinstance(arg1, Attribute):
            a = cgen.get_arg(arg1)
            if a is None:
                raise ValueError("Argument %s doesn't exist!" % name)
            if type(a) == IntArg:
                if type(arg2) == IntArg:
                    reg = general.pop()
                    code += load_int_into_reg(cgen, reg, arg1, ptr_reg)
                elif type(arg2) == FloatArg:
                    to_reg = xmm.pop()
                    code += load_int_into_reg(cgen, ptr_reg2, arg1, ptr_reg)
                    code += convert_int_to_float(ptr_reg2, to_reg)
                else:
                    raise ValueError("Type mismatch", a, arg2)
            elif type(a) == FloatArg and type(arg2) == FloatArg:
                reg = xmm.pop()
                code += load_float_into_reg(cgen, reg, arg1, ptr_reg)
            elif type(a) == Vector3Arg and type(arg2) == Vector3Arg:
                reg = xmm.pop()
                code += load_vec3_into_reg(cgen, reg, arg1, ptr_reg)
            elif type(a) == StructArg and type(arg2) == StructArg:
                reg = general.pop()
                if bits == '64bit':
                    reg = 'r' + reg[1:]
                    c, dummy, dummy = load_struct_ptr(cgen, arg1, reg)
                else:
                    c, dummy, dummy = load_struct_ptr(cgen, arg1, reg)
                code += c
            else:
                raise ValueError("Unsuported argument type, mismatch", a, arg2)
        else:
            raise ValueError("Unsupprted argument for shader!", arg1, arg2)
    return code


class Statement:
    def __init__(self):
        pass
    
    def asm_code(self):
        raise NotImplementedError()

class StmAssignName(Statement):
    def __init__(self, cgen, dest, src, unary=None):
        self.cgen = cgen
        self.dest = dest
        self.src = src
        self.unary = unary

    def asm_code(self):
        #source argument must exist
        src_arg = self.cgen.get_arg(self.src)
        if src_arg is None:
            raise ValueError('Source argument %s doesnt exist' % self.src)
        dst_arg = self.cgen.create_arg(self.dest, self.src)

        if isinstance(src_arg, IntArg) and isinstance(dst_arg, IntArg):
            code = copy_int_to_int(self.cgen, self.dest, self.src, self.unary)
        elif isinstance(src_arg, FloatArg) and isinstance(dst_arg, FloatArg):
            code = copy_float_to_float(self.cgen, self.dest, self.src, self.unary)
        elif isinstance(src_arg, Vector3Arg) and isinstance(dst_arg, Vector3Arg):
            code = copy_vec3_to_vec3(self.cgen, self.dest, self.src, self.unary)
        elif isinstance(src_arg, IntArg) and isinstance(dst_arg, FloatArg):
            code = copy_int_to_float(self.cgen, self.dest, self.src, self.unary)
        else:
            raise ValueError('Type mismatch', src_arg, dst_arg)
        return code

class StmAssignConst(Statement):
    def __init__(self, cgen, dest, const):
        self.cgen = cgen
        self.dest = dest
        self.const = const 

    def asm_code(self):
        arg = self.cgen.create_arg(self.dest, self.const)
        typ = type(arg)
        if typ == IntArg:
            if not isinstance(self.const, int):
                raise ValueError('Type mismatch', typ, self.const)
            code = store_const_into_mem(self.cgen, self.dest, self.const)
        elif typ == FloatArg:
            tmp = float(self.const) if isinstance(self.const, int) else self.const 
            if not isinstance(tmp, float):
                raise ValueError('Type mismatch', typ, self.const)
            code = store_const_into_mem(self.cgen, self.dest, tmp)
        elif typ == Vector3Arg:
            if (isinstance(self.const, tuple) or isinstance(self.const, list)) and len(self.const) == 3:
                code = store_const_into_mem(self.cgen, self.dest, float(self.const[0]))
                code += store_const_into_mem(self.cgen, self.dest, float(self.const[1]), offset=4)
                code += store_const_into_mem(self.cgen, self.dest, float(self.const[2]), offset=8)
                code += store_const_into_mem(self.cgen, self.dest, 0.0, offset=12)
            else:
                raise ValueError('Type mismatch',  arg, self.const)
        else:
            raise ValueError('Unknown type of destination', arg, self.const)
        return code


def load_argument(cgen, arg, op):
    if isinstance(arg, IntArg):
        reg = cgen.register(typ='general')
        code = load_int_into_reg(cgen, reg, op)
        typ = IntArg
    elif isinstance(arg, FloatArg):
        reg = cgen.register(typ='xmm')
        code = load_float_into_reg(cgen, reg, op)
        typ = FloatArg
    elif isinstance(arg, Vector3Arg):
        reg = cgen.register(typ='xmm')
        code = load_vec3_into_reg(cgen, reg, op)
        typ = Vector3Arg
    else:
        raise ValueError("Unknown argument", arg)
    return (code, reg, typ)

def load_operand(cgen, op):
    if isinstance(op, int):
        reg = cgen.register(typ='general')
        code = "mov %s, %i\n" % (reg, op)
        typ = IntArg 
    elif isinstance(op, float):
        con_arg = cgen.create_const(op)
        reg = cgen.register(typ='xmm')
        code = load_float_into_reg(cgen, reg, con_arg.name)
        typ = FloatArg
    elif isinstance(op, str) or isinstance(op, Attribute):
        arg = cgen.get_arg(op)
        if arg is None:
            raise ValueError("Operand doesn't exist", op)
        code, reg, typ = load_argument(cgen, arg, op)
    else:
        raise ValueError("Unknown operand")
    return (code, reg, typ)

def perform_operation_ints(cgen, reg1, reg2, operator):
    if operator == '+':
        code = 'add %s, %s\n' % (reg1, reg2)
        return code, reg1
    elif operator == '-':
        code = 'sub %s, %s\n' % (reg1, reg2)
        return code, reg1
    elif operator == '%' or operator == '/': #TODO test 64-bit implementation is needed
        epilog = """
        push eax
        push edx
        push esi
        """
        line1 = "mov eax, %s\n" % reg1
        line2 = "mov esi, %s\n" % reg2
        line3 = "xor edx, edx\n"
        line4 = "idiv esi\n"
        line5 = "pop esi\n"
        if operator == '/':
            line6 = "pop edx\n"
            line7 = "mov %s, eax\n" % reg1
            if reg1 == 'eax':
                line8 = "add esp, 4\n"
            else:
                line8 = "pop eax\n"
        else:
            line6 = "mov %s, edx\n" % reg1
            if reg1 == 'edx':
                line7 = "add esp, 4\n"
            else:
                line7 = "pop edx\n"
            if reg1 == 'eax':
                line8 = "add esp, 4\n"
            else:
                line8 = "pop eax\n"
        code = epilog + line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
        return code, reg1
    elif operator == '*':
        code = "imul %s, %s\n" % (reg1, reg2)
        return code, reg1
    else:
        raise ValueError("Unsuported operator", operator)

def perform_operation_floats(cgen, reg1, reg2, operator):
    if operator == '+':
        code = "addss %s, %s \n" % (reg1, reg2)
    elif operator == '-':
        code = "subss %s, %s \n" % (reg1, reg2)
    elif operator == '/':
        code = "divss %s, %s \n" % (reg1, reg2)
    elif operator == '*':
        code = "mulss %s, %s \n" % (reg1, reg2)
    else:
        raise ValueError("Unsuported operator", operator)
    return code, reg1

def perform_operation_int_float(cgen, reg1, reg2, operator):
    reg3 = cgen.register(typ="xmm")
    conversion = convert_int_to_float(reg1, reg3)
    code, reg = perform_operation_floats(cgen, reg3, reg2, operator)
    code = conversion + code
    return code, reg

def perform_operation_float_int(cgen, reg1, reg2, operator):
    reg3 = cgen.register(typ="xmm")
    conversion = convert_int_to_float(reg2, reg3)
    code, reg = perform_operation_floats(cgen, reg1, reg3, operator)
    code = conversion + code
    return code, reg

def perform_operation_vectors3(cgen, reg1, reg2, operator):
    if operator == '+':
        code = "addps %s, %s \n" % (reg1, reg2)
    elif operator == '-':
        code = "subps %s, %s \n" % (reg1, reg2)
    elif operator == '/':
        code = "divps %s, %s \n" % (reg1, reg2)
    elif operator == '*':
        code = "mulps %s, %s \n" % (reg1, reg2)
    else:
        raise ValueError("Unsuported operator", operator)
    return code, reg1

def perform_operation_float_vector(cgen, reg1, reg2, operator):
    line1 = "shufps %s, %s, 0x00\n" % (reg1, reg1)
    if operator == '*':
        code = "mulps %s, %s \n" % (reg1, reg2)
    else:
        raise ValueError("Unsuported operator", operator, reg1, reg2)
    code = line1 + code
    return code, reg1

def perform_operation_vector_float(cgen, reg1, reg2, operator):
    line1 = "shufps %s, %s, 0x00\n" % (reg2, reg2)
    if operator == '*':
        code = "mulps %s, %s \n" % (reg1, reg2)
    else:
        raise ValueError("Unsuported operator", operator, reg1, reg2)
    code = line1 + code
    return code, reg1

def perform_operation_int_vector(cgen, reg1, reg2, operator):
    reg3 = cgen.register(typ="xmm")
    conversion = convert_int_to_float(reg1, reg3)
    broadcast = "shufps %s, %s, 0x00\n" % (reg3, reg3)
    if operator == '*':
        code = "mulps %s, %s \n" % (reg3, reg2)
    else:
        raise ValueError("Unsuported operator", operator, reg1, reg2)
    code = conversion + broadcast + code
    return code, reg3

def perform_operation_vector_int(cgen, reg1, reg2, operator):
    reg3 = cgen.register(typ="xmm")
    conversion = convert_int_to_float(reg2, reg3)
    broadcast = "shufps %s, %s, 0x00\n" % (reg3, reg3)
    if operator == '*':
        code = "mulps %s, %s \n" % (reg1, reg3)
    else:
        raise ValueError("Unsuported operator", operator, reg1, reg2)
    code = conversion + broadcast + code
    return code, reg1

def perform_operation(cgen, reg1, typ1, operator, reg2, typ2):
    if typ1 == IntArg and typ2 == IntArg:
        code, reg = perform_operation_ints(cgen, reg1, reg2, operator)
        return (code, reg, IntArg)
    elif typ1 == FloatArg and typ2 == FloatArg:
        code, reg = perform_operation_floats(cgen, reg1, reg2, operator)
        return (code, reg, FloatArg)
    elif typ1 == IntArg and typ2 == FloatArg:
        code, reg = perform_operation_int_float(cgen, reg1, reg2, operator)
        return (code, reg, FloatArg)
    elif typ1 == FloatArg and typ2 == IntArg:
        code, reg = perform_operation_float_int(cgen, reg1, reg2, operator)
        return (code, reg, FloatArg)
    elif typ1 == Vector3Arg and typ2 == Vector3Arg:
        code, reg = perform_operation_vectors3(cgen, reg1, reg2, operator)
        return (code, reg, Vector3Arg)
    elif typ1 == FloatArg and typ2 == Vector3Arg:
        code, reg = perform_operation_float_vector(cgen, reg1, reg2, operator)
        return (code, reg, Vector3Arg)
    elif typ1 == Vector3Arg and typ2 == FloatArg:
        code, reg = perform_operation_vector_float(cgen, reg1, reg2, operator)
        return (code, reg, Vector3Arg)
    elif typ1 == IntArg and typ2 == Vector3Arg:
        code, reg = perform_operation_int_vector(cgen, reg1, reg2, operator)
        return (code, reg, Vector3Arg)
    elif typ1 == Vector3Arg and typ2 == IntArg:
        code, reg = perform_operation_vector_int(cgen, reg1, reg2, operator)
        return (code, reg, Vector3Arg)
    else:
        raise ValueError('Unknown combination of operands', typ1, typ2)

def gen_arithmetic_operation(cgen, op1, operator, op2):
    code1, reg1, typ1 = load_operand(cgen, op1)
    code2, reg2, typ2 = load_operand(cgen, op2)
    code3, reg, typ3 = perform_operation(cgen, reg1, typ1, operator, reg2, typ2)
    code = code1 + code2 + code3
    return (code, reg, typ3)

def gen_arithmetic_operation1(cgen, op1, operator, reg, typ):
    code1, reg1, typ1 = load_operand(cgen, op1)
    code2, reg2, typ2 = perform_operation(cgen, reg1, typ1, operator, reg, typ)
    code = code1 + code2
    return (code, reg2, typ2)

def gen_arithmetic_operation2(cgen, reg, typ, operator, op1):
    code1, reg1, typ1 = load_operand(cgen, op1)
    code2, reg2, typ2 = perform_operation(cgen, reg, typ, operator, reg1, typ1)
    code = code1 + code2
    return (code, reg2, typ2)

def is_operator(op):
    ops = ('+', '-', '/', '%', '*')
    return op in ops

class StmAssignExpression(Statement):
    def __init__(self, cgen, dest, operands):
        self.cgen = cgen
        self.dest = dest
        self.operands = operands

    def asm_code(self):
        op1, operator, op2 = self.operands[0]
        if isinstance(op1, Function) or isinstance(op2, Function):
            raise ValueError("Handle function of argument, save temporary register, variables etc...")
        code, reg, typ = gen_arithmetic_operation(self.cgen, op1, operator, op2)
        for comp in self.operands[1:]:
            if len(comp) == 1:
                operator = comp 
                raise ValueError("Not yet implemented")
            elif len(comp) == 2:
                if is_operator(comp[0]): # ('-', 'p.m')
                    if isinstance(comp[1], Function):
                        raise ValueError("Not yet implemented")
                    code2, reg, typ = gen_arithmetic_operation2(self.cgen, reg, typ, comp[0], comp[1])
                else: # ('p.m', '-')
                    if isinstance(comp[0], Function):
                        raise ValueError("Not yet implemented")
                    code2, reg, typ = gen_arithmetic_operation1(self.cgen, comp[0], comp[1], reg, typ)
                code += code2
            elif len(comp) == 3:
                op1, operator, op2 = comp 
                raise ValueError("Not yet implemented")
            else:
                raise ValueError("Unsuported number arguments in expression")

        dst = self.cgen.get_arg(self.dest)
        if dst is None:
            dst = self.cgen.create_arg(self.dest, typ=typ)

        self.cgen.clear_regs()
        reg = self.cgen.register(reg=reg)
        if typ == IntArg and type(dst) == IntArg:
            store = store_int_from_reg(self.cgen, reg, self.dest)
        elif typ == FloatArg and type(dst) == FloatArg:
            store = store_float_from_reg(self.cgen, reg, self.dest)
        elif type(dst) == FloatArg and typ == IntArg:
            to_reg = self.cgen.register(typ='xmm')
            store = convert_int_to_float(reg, to_reg)
            store += store_float_from_reg(self.cgen, to_reg, self.dest)
        elif typ == Vector3Arg and type(dst) == Vector3Arg:
            store = store_vec3_from_reg(self.cgen, reg, self.dest)
        elif typ == StructArg:
            raise ValueError("Unsupported argument returned type!", typ, dst)
        else:
            raise ValueError("Type mismatch", typ, dst)

        return code + store

class StmCall(Statement):
    def __init__(self, cgen, func, args):
        self.cgen = cgen
        self.func = func
        self.args = args

    def asm_code(self):
        if not self.cgen.func_exist(self.func):
            raise ValueError("Function %s doesnt exist!" % self.func)

        input_args = self.cgen.input_args(self.func)
        
        arguments = []
        for a in self.args:
            arg = self.cgen.fetch_argument(a)
            if arg is None:
                raise ValueError("Argument %s doesnt exist!", a)
            arguments.append(arg)

        if len(input_args) != len(arguments):
            raise ValueError("Argument lengtsh doesnt match", input_args, arguments)
        
        for arg1, arg2 in zip(input_args, arguments):
            if type(arg1) != type(arg2):
                raise ValueError("Argument type mismatch", arg1, arg2)

        code = _copy_to_regs_old(arguments)
        code += "call %s\n" % self.func
        return code

def make_call(cgen, function):
    name = function.name
    args = function.args

    cgen.clear_regs()

    f = cgen.get_function(name)
    if f is not None:
        func, ret_type = f
        code = func(cgen, args)

    s = cgen.get_shader(name)
    if s is not None:
        code = _copy_to_regs(cgen, args, s.input_args)
        code += "call %s\n" % name
        ret_type = s.ret_type

    if f is None and s is None:
        raise ValueError("Both function and shader doesnt exist")
    return (code, ret_type)



class StmAssignCall(Statement):
    def __init__(self, cgen, dest, function):
        self.cgen = cgen
        self.dest = dest
        self.function = function

    def asm_code(self):

        if not isinstance(self.function, Function):
            raise ValueError("Wrong argument, Function object is expected.")
        
        if self.cgen.is_user_type(self.function.name): #create new structure argument
            dst = self.cgen.get_arg(self.dest)
            if isinstance(dst, StructArg):
                if dst.typ.typ != self.function.name:
                    raise ValueError("Mismatch type ", dst, self.function, name)
            elif dst is None:
                dst = self.cgen.create_arg(self.dest, typ=self.function.name)
            else:
                raise ValueError("Mismatch types", self.dest, dst)
            return ''

        code, ret_type = make_call(self.cgen, self.function)

        dst = self.cgen.get_arg(self.dest)
        if dst is None:
            dst = self.cgen.create_arg(self.dest, typ=ret_type)

        self.cgen.clear_regs()
        if ret_type == IntArg and type(dst) == IntArg:
            reg = self.cgen.register(reg="eax")
            store = store_int_from_reg(self.cgen, reg, self.dest)
        elif ret_type == FloatArg and type(dst) == FloatArg:
            reg = self.cgen.register(reg="xmm0")
            store = store_float_from_reg(self.cgen, reg, self.dest)
        elif type(dst) == FloatArg and ret_type == IntArg:
            reg = self.cgen.register(reg="eax")
            to_reg = self.cgen.register(reg="xmm0")
            store = convert_int_to_float(reg, to_reg)
            store += store_float_from_reg(self.cgen, to_reg, self.dest)
        elif ret_type == Vector3Arg and type(dst) == Vector3Arg:
            reg = self.cgen.register(reg="xmm0")
            store = store_vec3_from_reg(self.cgen, reg, self.dest)
        elif ret_type == StructArg:
            raise ValueError("Unsupported argument returned type!", ret_type, dst)
        else:
            raise ValueError("Type mismatch", ret_type, dst)
        return code + store

class StmReturn(Statement):
    def __init__(self, cgen, const=None, src=None):
        self.cgen = cgen
        self.const = const
        self.src = src

    def asm_code(self):
        if self.const is None and self.src is None:
            return "ret \n"
        if self.const is not None:
            if isinstance(self.const, int):
                self.cgen.register_ret_type(IntArg)
                code = "mov eax, %i \n" % self.const
                code += "ret \n"
                return code
            elif isinstance(self.const, float):
                self.cgen.register_ret_type(FloatArg)
                raise ValueError("Argument const float ", self.const)
            elif isinstance(self.const, tuple) or isinstance(self.const, list):
                raise ValueError("Return is const list or tuple ", self.const)
            else:
                raise ValueError("Unsuported constant", self.const)
        arg = self.cgen.get_arg(self.src)
        if arg is None:
            raise ValueError("Argument doesnt exist.", self.src)
        self.cgen.register_ret_type(type(arg))
        self.cgen.clear_regs()
        if isinstance(arg, IntArg):
            reg = self.cgen.register(reg="eax")
            code = load_int_into_reg(self.cgen, reg, self.src)
        elif isinstance(arg, FloatArg):
            reg = self.cgen.register(reg="xmm0")
            code = load_float_into_reg(self.cgen, reg, self.src)
        elif isinstance(arg, Vector3Arg):
            reg = self.cgen.register(reg="xmm0")
            code = load_vec3_into_reg(self.cgen, reg, self.src)
        else:
            raise ValueError("Unsuported return argument!", arg)
        code += "ret \n"
        return code

def _int_function(cgen, args):
    if len(args) == 0:
        return "mov eax, 0\n"
    if len(args) != 1:
        raise ValueError("Wrong number of arguments", args)
    arg = args[0]
    if isinstance(arg, int):
        return "mov eax, %i\n" % arg
    elif isinstance(arg, float):
        return "mov eax, %i\n" % int(arg)
    elif isinstance(arg, str) or isinstance(arg, Attribute):
        cgen.clear_regs()
        a = cgen.get_arg(arg)
        if a is None:
            raise ValueError("Argument %s doesn't exist!" % name)
        if isinstance(a, IntArg):
            reg = cgen.register(reg="eax")
            code = load_int_into_reg(cgen, reg, arg)
            return code
        elif isinstance(a, FloatArg):
            reg = cgen.register(reg="xmm0")
            to_reg = cgen.register(reg="eax")
            code = load_float_into_reg(cgen, reg, arg)
            code += convert_float_to_int(reg, to_reg)
            return code
        else:
            raise ValueError("Unsupprted argument for int function!", a)
    else:
        raise ValueError('Unsupported argument')

register_function('int', _int_function, IntArg) 


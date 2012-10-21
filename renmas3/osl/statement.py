import struct
import platform
from .arg import Integer, Float, Vec3, Struct, Attribute
from .arg import Operands, Callable
from .cgen import register_function

from .instr import load_struct_ptr
from .instr import load_int_into_reg, load_float_into_reg, load_vec3_into_reg
from .instr import store_int_from_reg, store_float_from_reg, store_vec3_from_reg
from .instr import store_const_into_mem, convert_float_to_int, convert_int_to_float
from .instr import load_operand, store_operand, negate_operand

class Statement:
    def __init__(self):
        pass
    
    def asm_code(self):
        raise NotImplementedError()

def is_num(obj):
    if isinstance(obj, int) or isinstance(obj, float):
        return True
    return False

def is_const(obj):
    if isinstance(obj, int) or isinstance(obj, float):
        return True
    if isinstance(obj, tuple) or isinstance(obj, list):
        for n in obj:
            if not is_num(n):
                return False
        return True
    return False

def is_identifier(obj):
    if isinstance(obj, str) or isinstance(obj, Attribute):
        return True
    return False

def assign_const_to_dest(cgen, dest, const):
    arg = cgen.create_arg(dest, const)
    if isinstance(arg, Integer) and isinstance(const, int):
        code = store_const_into_mem(cgen, dest, const)
    elif isinstance(arg, Float) and (isinstance(const, int) or isinstance(const, float)):
        code = store_const_into_mem(cgen, dest, float(const))
    elif isinstance(arg, Vec3):
        if (isinstance(const, tuple) or isinstance(const, list)) and len(const) == 3:
            code = store_const_into_mem(cgen, dest, float(const[0]))
            code += store_const_into_mem(cgen, dest, float(const[1]), offset=4)
            code += store_const_into_mem(cgen, dest, float(const[2]), offset=8)
            code += store_const_into_mem(cgen, dest, 0.0, offset=12)
        else:
            raise ValueError('It is suposed to vector3 constant! Type mismatch!',  arg, const)
    else:
        raise ValueError('Unsuported constant', arg, const)
    return code

def assign_identifier(cgen, dest, src, unary=None):
    code1, reg, typ = load_operand(cgen, src)
    code2, reg = negate_operand(cgen, unary, reg, typ)
    code3 = store_operand(cgen, dest, reg, typ)
    return code1 + code2 + code3

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
    if typ1 == Integer and typ2 == Integer:
        code, reg = perform_operation_ints(cgen, reg1, reg2, operator)
        return (code, reg, Integer)
    elif typ1 == Float and typ2 == Float:
        code, reg = perform_operation_floats(cgen, reg1, reg2, operator)
        return (code, reg, Float)
    elif typ1 == Integer and typ2 == Float:
        code, reg = perform_operation_int_float(cgen, reg1, reg2, operator)
        return (code, reg, Float)
    elif typ1 == Float and typ2 == Integer:
        code, reg = perform_operation_float_int(cgen, reg1, reg2, operator)
        return (code, reg, Float)
    elif typ1 == Vec3 and typ2 == Vec3:
        code, reg = perform_operation_vectors3(cgen, reg1, reg2, operator)
        return (code, reg, Vec3)
    elif typ1 == Float and typ2 == Vec3:
        code, reg = perform_operation_float_vector(cgen, reg1, reg2, operator)
        return (code, reg, Vec3)
    elif typ1 == Vec3 and typ2 == Float:
        code, reg = perform_operation_vector_float(cgen, reg1, reg2, operator)
        return (code, reg, Vec3)
    elif typ1 == Integer and typ2 == Vec3:
        code, reg = perform_operation_int_vector(cgen, reg1, reg2, operator)
        return (code, reg, Vec3)
    elif typ1 == Vec3 and typ2 == Integer:
        code, reg = perform_operation_vector_int(cgen, reg1, reg2, operator)
        return (code, reg, Vec3)
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

def generate_arithmetic(cgen, src): #TODO --draw automat diagram then refacotr this
    operands = src.operands
    op1, operator, op2 = operands[0]
    code, reg, typ = gen_arithmetic_operation(cgen, op1, operator, op2)
    for comp in operands[1:]:
        if len(comp) == 1:
            operator = comp 
            raise ValueError("Not yet implemented")
        elif len(comp) == 2:
            if is_operator(comp[0]): # ('-', 'p.m')
                if isinstance(comp[1], Callable):
                    raise ValueError("Not yet implemented")
                code2, reg, typ = gen_arithmetic_operation2(cgen, reg, typ, comp[0], comp[1])
            else: # ('p.m', '-')
                if isinstance(comp[0], Callable):
                    raise ValueError("Not yet implemented")
                code2, reg, typ = gen_arithmetic_operation1(cgen, comp[0], comp[1], reg, typ)
            code += code2
        elif len(comp) == 3:
            op1, operator, op2 = comp 
            raise ValueError("Not yet implemented")
        else:
            raise ValueError("Unsuported number arguments in expression")
    return code, reg, typ

class StmExpression(Statement):
    def __init__(self, cgen, src):
        self.cgen = cgen
        self.src = src

    def asm_code(self):
        if isinstance(self.src, Callable):
            if self.cgen.is_user_type(self.src):
                return ValueError("User type illegal expression")
            else:
                code, reg, typ = self.cgen.generate_callable(self.src)
                return code
        else:
            return ValueError("Wrong expression")

def unary_number(n, unary):
    if unary is None or unary != '-':
        return n
    if isinstance(n, int):
        return int(unary + str(n))
    elif isinstance(n, float):
        return float(unary + str(n))
    else:
        raise ValueError("Unknown unary number", n, unary)

class StmAssign(Statement):
    def __init__(self, cgen, dest, src, unary=None):
        self.cgen = cgen
        self.dest = dest
        self.src = src
        self.unary = unary

    def asm_code(self):
        if is_const(self.src):
            code = assign_const_to_dest(self.cgen, self.dest, unary_number(self.src, self.unary))
        elif is_identifier(self.src):
            code = assign_identifier(self.cgen, self.dest, self.src, self.unary)
        elif isinstance(self.src, Operands):
            code, reg, typ = generate_arithmetic(self.cgen, self.src)
            code2, reg = negate_operand(self.cgen, self.unary, reg, typ)
            code += code2 + store_operand(self.cgen, self.dest, reg, typ)
        elif isinstance(self.src, Callable):
            if self.cgen.is_user_type(self.src):
                self.cgen.create_arg(self.dest, self.src)
                return ''
            code, reg, typ = self.cgen.generate_callable(self.src)
            if typ is not None:
                code2, reg = negate_operand(self.cgen, self.unary, reg, typ)
                code += code2 + store_operand(self.cgen, self.dest, reg, typ)
            else:
                raise ValueError("Callable doenst return value!!!", self.src.name)
        else:
            raise ValueError("Unknown source expression.", self.dest, self.src)
        return code

class StmReturn(Statement):
    def __init__(self, cgen, src):
        self.cgen = cgen
        self.src = src

    def asm_code(self):
        if is_const(self.src) or is_identifier(self.src):
            code, reg, typ = load_operand(self.cgen, self.src)
        elif isinstance(self.src, Operands):
            code, reg, typ = generate_arithmetic(self.cgen, self.src)
        elif isinstance(self.src, Callable):
            if self.cgen.is_user_type(self.src):
                raise ValueError("User type is not allowed in return", self.src)
            else:
                code, reg, typ = self.cgen.generate_callable(self.src)
        else:
            raise ValueError("Unsuported operand in return", self.src)
        self.cgen.register_ret_type(typ)

        xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        line = ''
        if reg in xmm:
            if reg != 'xmm0':
                line = 'movaps xmm0, %s\n' % reg
        else:
            if reg != 'eax':
                line = "mov eax, %s\n" % reg
        line2 = "ret\n"
        return code + line + line2
            

def generate_compare_ints(label, reg1, con, reg2):
    #if condition is met not jump to end of if
    line1 = "cmp %s, %s\n" % (reg1, reg2)
    if con == '==':
        line2 = "jne %s\n" % label
    elif con == '<':
        line2 = "jge %s\n" % label
    elif con == '>':
        line2 = "jle %s\n" % label
    elif con == '<=':
        line2 = "jg %s\n" % label
    elif con == '>=':
        line2 = "jl %s\n" % label
    elif con == '!=':
        line2 = "je %s\n" % label
    else:
        raise ValueError("Unknown condition operator", con)
    return line1 + line2 

def generate_compare_floats(label, reg1, con, reg2):
    line1 = "comiss %s, %s\n" % (reg1, reg2)
    if con == '==':
        line2 = "jnz %s\n" % label
    elif con == '<':
        line2 = "jnc %s\n" % label
    elif con == '>':
        line2 = "jc %s\n" % label
    elif con == '!=':
        line2 = "jz %s\n" % label
    else:
        raise ValueError("Unknown condition operator for floats", con)
    return line1 + line2

def generate_test(label, cgen, test):
    if len(test) != 1:
        raise ValueError("complex test for comaprison, not suported yet", test)
    con1 = test[0]
    if len(con1) == 1:
        op = con1[0]
        code, reg, typ = load_operand(cgen, op)
        if typ == Integer:
            line1 = "cmp %s, 0\n" % reg
            line2 = "je %s\n" % label
            code += line1 + line2
        else:
            raise ValueError("Not yet suported that type of operand", op, typ)
    elif len(con1) == 3:
        left_op, con, right_op = con1
        code1, reg1, typ1 = load_operand(cgen, left_op)
        code2, reg2, typ2 = load_operand(cgen, right_op)
        if typ1 == Integer and typ2 == Integer:
            code3 = generate_compare_ints(label, reg1, con, reg2)
            code = code1 + code2 + code3
        elif typ1 == Float and typ2 == Float:
            code3 = generate_compare_floats(label, reg1, con, reg2)
            code = code1 + code2 + code3
        elif typ1 == Integer and typ2 == Float:
            to_reg = cgen.register(typ='xmm')
            conv = convert_int_to_float(reg1, to_reg)
            code3 = generate_compare_floats(label, to_reg, con, reg2)
            code = code1 + code2 + conv + code3
        elif typ1 == Float and typ2 == Integer:
            to_reg = cgen.register(typ='xmm')
            conv = convert_int_to_float(reg2, to_reg)
            code3 = generate_compare_floats(label, reg1, con, to_reg)
            code = code1 + code2 + conv + code3
        else:
            raise ValueError("Unsported type for comparison", typ1, typ2)
    else:
        raise ValueError("Not yet suported that test!")
    return code

class StmIf(Statement):
    def __init__(self, cgen, body, test, orelse=None):
        self.cgen = cgen
        self.body = body
        self.test = test
        self.orelse = orelse

    def asm_code(self):
        if_label = 'if_' + str(id(self))
        orelse_label = 'orelse_' + str(id(self))
        endif_label = 'endif_' + str(id(self))

        if self.orelse is not None:
            code = generate_test(orelse_label, self.cgen, self.test)
        else:
            code = generate_test(if_label, self.cgen, self.test)

        for i in self.body:
            self.cgen.clear_regs()
            code += i.asm_code()

        if self.orelse is not None:
            code += "jmp %s\n" % endif_label
            code += "%s:\n" % orelse_label
            for i in self.orelse:
                self.cgen.clear_regs()
                code += i.asm_code()
            code += "%s:\n" % endif_label
        else:
            code += "%s:\n" % if_label
        return code

class StmBreak(Statement):
    def __init__(self, label):
        if label is None:
            raise ValueError("Break statement out of loop!")
        self.label = label

    def asm_code(self):
        return "jmp %s\n" % self.label


class StmWhile(Statement):
    def __init__(self, cgen, body, test):
        self.cgen = cgen
        self.body = body
        self.test = test

    def asm_code(self):
        begin_label = 'while_' + str(id(self))
        end_label = 'endwhile_' + str(id(self))

        code = "%s:\n" % begin_label
        code += generate_test(end_label, self.cgen, self.test)
        for i in self.body:
            self.cgen.clear_regs()
            code += i.asm_code()
        code += "jmp %s\n" % begin_label
        code += "%s:\n" % end_label
        return code

    def label(self):
        end_label = 'endwhile_' + str(id(self))
        return end_label


import platform
from .arg import Integer, Float, Vec3, Vec2, Vec4, Struct, Attribute, Operation
from .arg import Operations, Callable, Name, Subscript, Const, EmptyOperand
from .arg import conv_int_to_float
from .cgen import register_function

from .instr import load_operand, store_operand
import renmas3.switch as proc

class Statement:
    def __init__(self):
        pass
    
    def asm_code(self, cgen):
        raise NotImplementedError()

def _filter_regs(xmms, general32, general64, ocupied_regs):
    for r in ocupied_regs:
        if r in xmms:
            xmms.remove(r)
        if r in general32:
            general32.remove(r)
        if r in general64:
            general64.remove(r)

def _move_to_free_reg(reg, ocupied_regs):
    if ocupied_regs is None:
        return '', None
    if reg not in ocupied_regs:
        return '', None
    xmms = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general32 = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    general64 = ['rbp', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rax']
    if reg in xmms:
        _filter_regs(xmms, general32, general64, ocupied_regs)
        free_reg = xmms.pop()
        if proc.AVX:
            code = "vmovaps %s, %s\n" % (free_reg, reg)
        else:
            code = "movaps %s, %s\n" % (free_reg, reg)
    elif reg in general32:
        _filter_regs(xmms, general32, general64, ocupied_regs)
        free_reg = general32.pop()
        code = "mov %s, %s\n" % (free_reg, reg)
    elif reg in general64:
        _filter_regs(xmms, general32, general64, ocupied_regs)
        free_reg = general64.pop()
        code = "mov %s, %s\n" % (free_reg, reg)
    else:
        raise ValueError("Unknown register. Cannot be saved.", reg)
    return code, free_reg 

def process_callable(cgen, op, ocupied_regs=None):
    if not isinstance(op, Callable):
        raise ValueError("Operand is not callable", op)
    if cgen.is_inline(op):
        code, reg, typ = cgen.generate_callable(op)
        return code, reg, typ
    else:
        code = ''
        if ocupied_regs is not None:
            code += cgen.save_regs(ocupied_regs)
        co, reg, typ = cgen.generate_callable(op)
        code += co
        co, reg2 = _move_to_free_reg(reg, ocupied_regs)
        code += co
        if ocupied_regs is not None:
            code += cgen.load_regs(ocupied_regs)
            for r in ocupied_regs:
                if r != reg:
                    cgen.register(reg=r)
        if reg2 is not None:
            cgen.register(reg=reg2)
            return code, reg2, typ
        else:
            return code, reg, typ

def process_operand(cgen, op, ocupied_regs=None):
    if isinstance(op, Callable):
        return process_callable(cgen, op, ocupied_regs)
    else: #Note --cgen.register(reg) is allocate in load command
        code, reg, typ = load_operand(cgen, op)
        return (code, reg, typ)

def process_operation(cgen, operation, stack=[]):
    def release_free_reg(dest, reg1, reg2):
        if dest != reg1:
            cgen.release_reg(reg1)
        if dest != reg2:
            cgen.release_reg(reg2)

    left = operation.left
    right = operation.right
    ocupied = [r for r, t in stack]
    if not left is EmptyOperand and not right is EmptyOperand:
        code, reg, typ = process_operand(cgen, operation.left, ocupied_regs=ocupied)
        ocupied.append(reg)
        code2, reg2, typ2 = process_operand(cgen, operation.right, ocupied_regs=ocupied)
        code += code2
    elif left is EmptyOperand and right is EmptyOperand:
        reg2, typ2 = stack.pop()
        reg, typ = stack.pop()
        code = ''
    elif left is EmptyOperand and not right is EmptyOperand:
        reg, typ = stack.pop()
        code, reg2, typ2 = process_operand(cgen, operation.right, ocupied_regs=ocupied)
    elif not left is EmptyOperand and right is EmptyOperand:
        code, reg, typ = process_operand(cgen, operation.left, ocupied_regs=ocupied)
        reg2, typ2 = stack.pop()
    else:
        raise ValueError("Operation is wrong!", operation)

    if typ.supported(operation.operator, typ2):
        code3, reg3, typ3 = typ.arith_cmd(cgen, reg, reg2, typ2, operation.operator)
    elif typ2.supported(operation.operator, typ):
        code3, reg3, typ3 = typ2.rev_arith_cmd(cgen, reg2, reg, typ, operation.operator)
    else:
        raise ValueError("Operation not suported", reg, typ, operation.operator, reg2, typ2)

    release_free_reg(reg3, reg, reg2)
    stack.append((reg3, typ3))
    return code + code3, reg3, typ3

def process_expression(cgen, expr, unary=None):
    if not isinstance(expr, Operations):
        code, reg, typ = process_operand(cgen, expr)
        if unary is not None and unary == '-':
            code += typ.neg_cmd(cgen, reg)
        return code, reg, typ
    #process operations and execute arithmetic
    #TODO -- unary -- negate first operand
    if unary is not None:
        raise ValueError("Not yet implemented. Unary expression")
    stack = []
    code = ''
    for operation in expr.operations:
        co, reg, typ = process_operation(cgen, operation, stack)
        code += co
    return code, reg, typ

class StmAssign(Statement):
    def __init__(self, dest, expr, unary=None):
        self.dest = dest
        self.expr = expr 
        self.unary = unary

    def asm_code(self, cgen):
        if isinstance(self.expr, Const): #little optimization
            arg = cgen.create_arg(self.dest, self.expr.const)
            if isinstance(self.dest, Name):
                code = arg.store_const(cgen, self.expr.const)
            elif isinstance(self.dest, Attribute):
                code = arg.store_attr_const(cgen, self.dest.path, self.expr.const)
            else:
                raise ValueError("Not supported destination of const!")
            return code
        elif isinstance(self.expr, Callable) and cgen.is_user_type(self.expr):
            cgen.create_arg(self.dest, self.expr)
            return ''
        else:
            code, reg, typ = process_expression(cgen, self.expr, self.unary)
            code2 = store_operand(cgen, self.dest, reg, typ)
            return code + code2

class StmExpression(Statement):
    def __init__(self, expr):
        self.expr = expr 

    def asm_code(self, cgen):
        code, reg, typ = process_expression(cgen, self.expr)
        return code

#TODO unary operator
class StmReturn(Statement):
    def __init__(self, expr):
        self.expr = expr 

    def asm_code(self, cgen):
        if self.expr is None:
            cgen.register_ret_type(Integer)
            return "ret\n"
        code, reg, typ = process_expression(cgen, self.expr)
        cgen.register_ret_type(typ)
        xmm = ('xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0')
        general = ('ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax')
        code2 = ''
        if reg in xmm and reg !='xmm0':
            if proc.AVX:
                code2 = 'vmovaps xmm0, %s\n' % reg
            else:
                code2 = 'movaps xmm0, %s\n' % reg
        if reg in general and reg != 'eax' and reg != 'rax':
            if reg in general:
                code2 = "mov eax, %s\n" % reg
            else:
                code2 = "mov rax, %s\n" % reg
        return code + code2 + "ret\n"

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
            conv = conv_int_to_float(cgen, reg1, to_reg)
            code3 = generate_compare_floats(label, to_reg, con, reg2)
            code = code1 + code2 + conv + code3
        elif typ1 == Float and typ2 == Integer:
            to_reg = cgen.register(typ='xmm')
            conv = conv_int_to_float(cgen, reg2, to_reg)
            code3 = generate_compare_floats(label, reg1, con, to_reg)
            code = code1 + code2 + conv + code3
        else:
            raise ValueError("Unsported type for comparison", typ1, typ2)
    else:
        raise ValueError("Not yet suported that test!")
    return code

class StmIf(Statement):
    def __init__(self, body, test, orelse=None):
        self.body = body
        self.test = test
        self.orelse = orelse

    def asm_code(self, cgen):
        if_label = 'if_' + str(id(self))
        orelse_label = 'orelse_' + str(id(self))
        endif_label = 'endif_' + str(id(self))

        if self.orelse is not None:
            code = generate_test(orelse_label, cgen, self.test)
        else:
            code = generate_test(if_label, cgen, self.test)

        for i in self.body:
            cgen.clear_regs()
            code += i.asm_code(cgen)

        if self.orelse is not None:
            code += "jmp %s\n" % endif_label
            code += "%s:\n" % orelse_label
            for i in self.orelse:
                cgen.clear_regs()
                code += i.asm_code(cgen)
            code += "%s:\n" % endif_label
        else:
            code += "%s:\n" % if_label
        return code

class StmBreak(Statement):
    def __init__(self, label):
        if label is None:
            raise ValueError("Break statement out of loop!")
        self.label = label

    def asm_code(self, cgen):
        return "jmp %s\n" % self.label


class StmWhile(Statement):
    def __init__(self, body, test):
        self.body = body
        self.test = test

    def asm_code(self, cgen):
        begin_label = 'while_' + str(id(self))
        end_label = 'endwhile_' + str(id(self))

        code = "%s:\n" % begin_label
        code += generate_test(end_label, cgen, self.test)
        for i in self.body:
            cgen.clear_regs()
            code += i.asm_code(cgen)
        code += "jmp %s\n" % begin_label
        code += "%s:\n" % end_label
        return code

    def label(self):
        end_label = 'endwhile_' + str(id(self))
        return end_label


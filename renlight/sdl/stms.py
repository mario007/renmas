
"""
    This module implement statements that shading language support.
"""

from .strs import Const, Callable
from .asm_cmds import process_expression, store_const, store_operand
from .asm_cmds import move_reg_to_acum, generate_test

class Statement:
    """
        Abstract base class that define interface for statements.
    """
    
    def asm_code(self, cgen):
        """
            Generate assembly code for this statement.
            @param cgen - code generator
        """
        raise NotImplementedError()


class StmAssign(Statement):
    def __init__(self, dest, expr):
        self.dest = dest
        self.expr = expr 

    def asm_code(self, cgen):
        if isinstance(self.expr, Const): #little optimization
            code = store_const(cgen, self.dest, self.expr)
            return code
        elif isinstance(self.expr, Callable) and cgen.is_user_type(self.expr):
            cgen.create_arg(self.dest, self.expr)
            return ''
        else:
            code, reg, typ = process_expression(cgen, self.expr)
            code2 = store_operand(cgen, self.dest, reg, typ)
            return code + code2


class StmExpression(Statement):
    def __init__(self, expr):
        self.expr = expr 

    def asm_code(self, cgen):
        code, reg, typ = process_expression(cgen, self.expr)
        return code


class StmReturn(Statement):
    def __init__(self, expr):
        self.expr = expr 

    def asm_code(self, cgen):
        if self.expr is None:
            cgen.register_ret_type(Integer)
            return "ret\n"
        code, reg, typ = process_expression(cgen, self.expr)
        cgen.register_ret_type(typ)
        code2 = move_reg_to_acum(cgen, reg, typ) 
        return code + code2 + "ret\n"


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
            code = generate_test(cgen, self.test, orelse_label)
        else:
            code = generate_test(cgen, self.test, if_label)
        code += ''.join(cgen.inst_code(i) for i in self.body)

        if self.orelse is not None:
            code += "jmp %s\n" % endif_label
            code += "%s:\n" % orelse_label
            code += ''.join(cgen.inst_code(i) for i in self.orelse)
            code += "%s:\n" % endif_label
        else:
            code += "%s:\n" % if_label
        return code


class StmWhile(Statement):
    def __init__(self, body, test):
        self.body = body
        self.test = test

    def asm_code(self, cgen):
        begin_label = 'while_' + str(id(self))
        end_label = 'endwhile_' + str(id(self))

        code = "%s:\n" % begin_label
        code += generate_test(cgen, self.test, end_label)
        code += ''.join(cgen.inst_code(i) for i in self.body)
        code += "jmp %s\n" % begin_label
        code += "%s:\n" % end_label
        return code

    def label(self):
        return 'endwhile_' + str(id(self))


class StmBreak(Statement):
    def __init__(self, label):
        self.label = label

    def asm_code(self, cgen):
        return "jmp %s\n" % self.label


class StmEmpty(Statement):

    def asm_code(self, cgen):
        return ''


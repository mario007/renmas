
"""
    This module implement statements that shading language support.
"""

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


class StmExpression(Statement):
    def __init__(self, expr):
        self.expr = expr 


class StmReturn(Statement):
    def __init__(self, expr):
        self.expr = expr 


class StmIf(Statement):
    def __init__(self, body, test, orelse=None):
        self.body = body
        self.test = test
        self.orelse = orelse


class StmBreak(Statement):
    def __init__(self, label):
        self.label = label


class StmWhile(Statement):
    def __init__(self, body, test):
        self.body = body
        self.test = test

    def label(self):
        return 'endwhile_' + str(id(self))


class StmEmpty(Statement):

    def asm_code(self, cgen):
        return ''


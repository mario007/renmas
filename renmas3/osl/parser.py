import ast

from .statement import StmAssignConst, StmAssignName, StmAssignBinary 
from .cgen import CodeGenerator

def operator(obj):
    if isinstance(obj, ast.Add):
        return '+'
    elif isinstance(obj, ast.Mult):
        return '*'
    elif isinstance(obj, ast.Sub):
        return '-'
    elif isinstance(obj, ast.Div):
        return '/'
    elif isinstance(obj, ast.Mod):
        return '%'
    else:
        raise ValueError("Unknown operator", obj)

class Parser:
    def __init__(self):
        pass

    def _simple_assigments(self, targets, obj):
        if isinstance(obj, ast.Num):
            n = obj.n
            if isinstance(n, int) or isinstance(n, float):
                for t in targets:
                    self.cgen.add_stm(StmAssignConst(self.cgen, t.id, n))
            else:
                raise ValueError('Unknow number type', type(n))
        elif isinstance(obj, ast.Name):
            for t in targets:
                self.cgen.add_stm(StmAssignName(self.cgen, t.id, obj.id))
        else:
            raise ValueError("Unknown assigment!", obj)
    
    def _binary_operation(self, targets, obj):
        left = obj.left
        right = obj.right
        if isinstance(left, ast.Num) and isinstance(right, ast.Num):
            op = operator(obj.op)
            for t in targets:
                self.cgen.add_stm(StmAssignBinary(self.cgen, t.id, left.n, right.n, op))
        elif isinstance(left, ast.Num) and isinstance(right, ast.Name):
            pass
        elif isinstance(left, ast.Name) and isinstance(right, ast.Num):
            pass
        elif isinstance(left, ast.Name) and isinstance(right, ast.Name):
            op = operator(obj.op)
            for t in targets:
                self.cgen.add_stm(StmAssignBinary(self.cgen, t.id, left.id, right.id, op))
        else:
            raise ValueError("Unsuported binary operation", left, right)

    def _parse_assign(self, assign):
        if isinstance(assign.value, ast.Num):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Name):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.BinOp):
            self._binary_operation(assign.targets, assign.value)
        elif isinstance(assign.value, ast.UnaryOp):
            raise ValueError('UnaryOp assign', assign.value)
        elif isinstance(assign.value, ast.Call):
            raise ValueError('Call assign', assign.value)
        elif isinstance(assign.value, ast.Subscript):
            raise ValueError('Subscript assign', assign.value)
        elif isinstance(assign.value, ast.Tuple):
            raise ValueError('Tuple assign', assign.value)
        elif isinstance(assign.value, ast.List):
            raise ValueError('List assign', assign.value)
        else:
            print('Unknown assign', assign.value)

    def _parse_statement(self, statement):
        if isinstance(statement, ast.Assign):
            self._parse_assign(statement)
        elif isinstance(statement, ast.For):
            raise ValueError('For statement', statement)
        elif isinstance(statement, ast.While):
            raise ValueError('While statement', statement)
        elif isinstance(statement, ast.Pass):
            raise ValueError('Pass statement', statement)
        elif isinstance(statement, ast.Expr):
            raise ValueError('Expr statement', statement)
        elif isinstance(statement, ast.If):
            raise ValueError('If statement', statement)
        else:
            raise ValueError('Uknown satement', statement)

    def parse(self, source, args):
        code = ast.parse(source)
        self.cgen = CodeGenerator(args)

        if isinstance(code, ast.Module):
            for statement in code.body:
                self._parse_statement(statement)
        else:
            raise ValueError('Source is not instance of ast.Module', code)

        return self.cgen


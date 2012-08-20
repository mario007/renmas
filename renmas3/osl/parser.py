import ast

from .statement import StmAssignName

class CodeBuilder:
    def __init__(self, args):
        self._args = args
        self._statements = []
        self._const_args = {}

    def add_stm(self, stm):
        pass

    def generate_code(self):
        pass

    def fetch_const(self, value):
        if value in self._const_args:
            return self._const_args[value]

class Parser:
    def __init__(self):
        pass

    def _simple_assigments(self, targets, obj):
        if isinstance(obj, ast.Num):
            n = obj.n
            if isinstance(n, int):
                print('Simple integer assigments')
            elif isinstance(n, float):
                print('Simple float assigments')
            else:
                raise ValueError('Unknow number type', type(n))
        elif isinstance(obj, ast.Name):
            print('Simple name assigments', obj.id)
        else:
            print ('Unknown', obj)
        print ('Targets', targets)

    def _parse_assign(self, assign):
        if isinstance(assign.value, ast.Num):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Name):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.BinOp):
            raise ValueError('BinarOp assign', assign.value)
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

        if isinstance(code, ast.Module):
            for statement in code.body:
                self._parse_statement(statement)
        else:
            raise ValueError('Source is not instance of ast.Module', code)


import ast

from .statement import StmAssignConst, StmAssignName, StmAssignBinary
from .statement import StmCall, StmAssignCall, StmReturn
from .arg import Callable, Attribute

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

def extract_numbers(obj):
    if isinstance(obj, ast.Tuple) or isinstance(obj, ast.List):
        nums = obj.elts
        numbers = []
        for n in nums:
            if isinstance(n, ast.Num):
                numbers.append(float(n.n))
            else:
                raise ValueError("Its not a constant", n)
        if isinstance(obj, ast.Tuple):
            return tuple(numbers)
        else:
            return numbers
    else:
        raise ValueError("Unknown type", obj)

def extract_path(obj):
    comps = []
    while isinstance(obj, ast.Attribute):
        comps.insert(0, obj.attr)
        obj = obj.value
    path = ".".join(comps)
    if isinstance(obj, ast.Name):
        name = obj.id
    else:
        raise ValueError("Unknown target name, maybe subscript!", obj)
    
    return (name, path)

def make_name(obj):
    if isinstance(obj, ast.Attribute):
        name, path = extract_path(obj)
        return Attribute(name, path)
    elif isinstance(obj, ast.Name):
        return obj.id
    else:
        raise ValueError("Unsuported source")

class Parser:
    def __init__(self):
        pass

    def _simple_assigments(self, targets, obj):
        if isinstance(obj, ast.Num):
            n = obj.n
            if isinstance(n, int) or isinstance(n, float):
                for t in targets:
                    if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                        self.cgen.add(StmAssignConst(self.cgen, make_name(t), n))
                    else:
                        raise ValueError("Unknown target", t)
            else:
                raise ValueError('Unknow number type', type(n))
        elif isinstance(obj, ast.Name):
            for t in targets:
                if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                    self.cgen.add(StmAssignName(self.cgen, make_name(t), obj.id))
                else:
                    raise ValueError("Unknown target", t)

        elif isinstance(obj, ast.Tuple) or isinstance(obj, ast.List):
            nums = extract_numbers(obj)
            for t in targets:
                if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                    self.cgen.add(StmAssignConst(self.cgen, make_name(t), nums))
                else:
                    raise ValueError("Unknown target", t)
        elif isinstance(obj, ast.Attribute):
            src, src_path = extract_path(obj)
            for t in targets:
                if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                    self.cgen.add(StmAssignName(self.cgen, make_name(t), Attribute(src, src_path)))
                else:
                    raise ValueError("Unknown target", t)
        elif isinstance(obj, ast.Call):
            func = obj.func.id
            args = []
            for arg in obj.args:
                if isinstance(arg, ast.Name) or isinstance(arg, ast.Attribute):
                    args.append(make_name(arg))
                elif isinstance(arg, ast.Num):
                    args.append(arg.n)
                else:
                    raise ValueError("Unsuported argument type", arg)
            for t in targets:
                if isinstance(t, ast.Name) or isinstance(t, ast.Attribute):
                    self.cgen.add(StmAssignCall(self.cgen, make_name(t), func, args))
                else:
                    raise ValueError("Unknown target", t)
        else:
            raise ValueError("Unknown assigment!", obj)
    
    def _binary_operation(self, targets, obj):
        left = obj.left
        right = obj.right
        if isinstance(left, ast.Num) and isinstance(right, ast.Num):
            op = operator(obj.op)
            for t in targets:
                self.cgen.add(StmAssignBinary(self.cgen, t.id, left.n, right.n, op))
        elif isinstance(left, ast.Num) and isinstance(right, ast.Name):
            pass
        elif isinstance(left, ast.Name) and isinstance(right, ast.Num):
            pass
        elif isinstance(left, ast.Name) and isinstance(right, ast.Name):
            op = operator(obj.op)
            for t in targets:
                self.cgen.add(StmAssignBinary(self.cgen, t.id, left.id, right.id, op))
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
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Subscript):
            raise ValueError('Subscript assign', assign.value)
        elif isinstance(assign.value, ast.Tuple):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.List):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Attribute):
            self._simple_assigments(assign.targets, assign.value)
        else:
            raise ValueError("Unknown assign", assign.value)

    def _parse_call(self, call):
        func = call.func.id
        args = []
        for arg in call.args:
            if isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Num):
                args.append(arg.n)
            elif isinstance(arg, ast.List):
                raise ValueError("Not yet implemented", arg)
            elif isinstance(arg, ast.Tuple):
                raise ValueError("Not yet implemented", arg)
            else:
                raise ValueError("Unsuported argument type", arg)

        self.cgen.add(StmCall(self.cgen, func, args))

    def _parse_return(self, obj):
        if isinstance(obj, ast.Num):
            self.cgen.add(StmReturn(self.cgen, const=obj.n))
        elif isinstance(obj, ast.Name):
            self.cgen.add(StmReturn(self.cgen, src=obj.id))
        elif isinstance(obj, ast.Attribute):
            name, path = extract_path(t)
            self.cgen.add(StmReturn(self.cgen, src=Attribute(name, path)))
        elif obj is None: #empty return statement
            self.cgen.add(StmReturn(self.cgen))
        else:
            raise ValueError("Unknown return object", obj)

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
            if isinstance(statement.value, ast.Call): # function call
                self._parse_call(statement.value)
            else:
                raise ValueError('Expr statement', statement, statement.value)
        elif isinstance(statement, ast.If):
            raise ValueError('If statement', statement)
        elif isinstance(statement, ast.Return):
            self._parse_return(statement.value)
        else:
            raise ValueError('Uknown satement', statement)

    def parse(self, source, cgen):
        code = ast.parse(source)
        self.cgen = cgen

        if isinstance(code, ast.Module):
            for statement in code.body:
                self._parse_statement(statement)
        else:
            raise ValueError('Source is not instance of ast.Module', code)

        return self.cgen


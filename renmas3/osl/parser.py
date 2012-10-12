import ast

from .statement import StmAssignConst, StmAssignName
from .statement import StmCall, StmAssignCall, StmReturn, StmAssignExpression
from .arg import Function, Attribute

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

def extract_unary(obj):
    if isinstance(obj, ast.USub):
        return '-'
    elif isinstance(obj, ast.UAdd):
        return '+'
    else:
        raise ValueError("Unknown unary operand", obj)

def extract_numbers(obj):
    if isinstance(obj, ast.Tuple) or isinstance(obj, ast.List):
        nums = obj.elts
        numbers = []
        for n in nums:
            if isinstance(n, ast.Num):
                numbers.append(float(n.n))
            elif isinstance(n, ast.UnaryOp):
                if isinstance(n.operand, ast.Num):
                    numbers.append(float(extract_unary(n.op) + str(n.operand.n)))
                else:
                    raise ValueError("Wrong operand in Unaray operator", n.operand)
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

def extract_operand(obj):
    if isinstance(obj, ast.Num):
        return obj.n
    elif isinstance(obj, ast.Name):
        return obj.id
    elif isinstance(obj, ast.Attribute):
        src, src_path = extract_path(obj)
        return Attribute(src, src_path)
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
        return Function(func, args)
    else:
        raise ValueError("Unsuported operand in binary arithmetic.")

def extract_operands(obj):
    op1 = extract_operand(obj.left)
    op2 = extract_operand(obj.right)
    o = operator(obj.op)
    return (op1, o, op2)

def parse_arithmetic(bin_op):
    left = bin_op.left
    right = bin_op.right
    op = bin_op.op

    #two operands version
    if not isinstance(left, ast.BinOp) and not isinstance(right, ast.BinOp):
        op1, o, op2 = extract_operands(bin_op)
        return [(op1, o, op2)]

    #min four operands version
    if isinstance(left, ast.BinOp) and isinstance(right, ast.BinOp):
        ops = []
        op1, o1, op2 = extract_operands(left)
        op3, o2, op4 = extract_operands(right)
        ops.append((op1, o1, op2))
        ops.append((op3, o2, op4))
        ops.append((operator(op),))
        return ops
        raise ValueError("Not yet implemented")

    # min three operands version
    if isinstance(left, ast.BinOp) or isinstance(right, ast.BinOp):
        ops = []
        if isinstance(left, ast.BinOp):
            if isinstance(left.left, ast.BinOp): #four operands version
                op1, o, op2 = extract_operands(left.left)
                ops.append((op1, o, op2))
                o = operator(left.op)
                op2 = extract_operand(left.right)
                ops.append((o, op2))
            elif isinstance(left.right, ast.BinOp):
                op1, o, op2 = extract_operands(left.right)
                ops.append((op1, o, op2))
                o = operator(left.op)
                op2 = extract_operand(left.left)
                ops.append((op2, o))
            else:
                op1, o, op2 = extract_operands(left)
                ops.append((op1, o, op2))
        if isinstance(right, ast.BinOp):
            if isinstance(right.left, ast.BinOp): # four operands version
                op1, o, op2 = extract_operands(right.left)
                ops.append((op1, o, op2))
                o = operator(right.op)
                op2 = extract_operand(right.right)
                ops.append((o, op2))
            elif isinstance(right.right, ast.BinOp):
                raise ValueError("Not yet implemented")
            else:
                op1, o, op2 = extract_operands(right)
                ops.append((op1, o, op2))

        o = operator(op)
        if not isinstance(left, ast.BinOp):
            op2 = extract_operand(left)
            ops.append((op2, o))
        if not isinstance(right, ast.BinOp):
            op2 = extract_operand(right)
            ops.append((o, op2))
        return ops
    raise ValueError("Two complex expression")

def unary_number(n, unary):
    if isinstance(n, int):
        return int(unary + str(n))
    elif isinstance(n, float):
        return float(unary + str(n))
    else:
        raise ValueError("Unknown unary number", n, unary)

class Parser:
    def __init__(self):
        pass

    def _simple_assigments(self, targets, obj, unary=None):
        if isinstance(obj, ast.Num):
            n = obj.n
            if isinstance(n, int) or isinstance(n, float):
                for t in targets:
                    if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                        if unary is not None:
                            n = unary_number(n, unary)
                        self.cgen.add(StmAssignConst(self.cgen, make_name(t), n))
                    else:
                        raise ValueError("Unknown target", t)
            else:
                raise ValueError('Unknow number type', type(n))
        elif isinstance(obj, ast.Name):
            for t in targets:
                if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                    self.cgen.add(StmAssignName(self.cgen, make_name(t), obj.id, unary))
                else:
                    raise ValueError("Unknown target", t)

        elif isinstance(obj, ast.Tuple) or isinstance(obj, ast.List):
            if unary is not None:
                raise ValueError("Unsuported constant with unary", unary, obj)
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
                    self.cgen.add(StmAssignName(self.cgen, make_name(t), Attribute(src, src_path), unary))
                else:
                    raise ValueError("Unknown target", t)
        elif isinstance(obj, ast.Call):
            if unary is not None:
                raise ValueError("Unary is not yet suported in function call assign!!!")
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
                    self.cgen.add(StmAssignCall(self.cgen, make_name(t), Function(func, args)))
                else:
                    raise ValueError("Unknown target", t)
        else:
            raise ValueError("Unknown assigment!", obj)
    
    def _binary_operation(self, targets, obj):
        expr = parse_arithmetic(obj)
        for t in targets:
            if isinstance(t, ast.Attribute) or isinstance(t, ast.Name):
                self.cgen.add(StmAssignExpression(self.cgen, make_name(t), expr))
            else:
                raise ValueError("Unknown target", t)

    def _parse_assign(self, assign):
        if isinstance(assign.value, ast.Num):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Name):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.BinOp):
            self._binary_operation(assign.targets, assign.value)
        elif isinstance(assign.value, ast.UnaryOp):
            op = extract_unary(assign.value.op)
            self._simple_assigments(assign.targets, assign.value.operand, op)
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

        raise ValueError("Call not yet properly implemented")
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


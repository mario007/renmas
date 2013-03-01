import ast

from .statement import StmIf, StmWhile, StmBreak
from .statement import StmReturn, StmExpression
from .statement import StmAssign
from .arg import Attribute, Operations, Callable, Name, Const, Subscript
from .arg import Operation, EmptyOperand

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

def unary_number(n, unary):
    if unary is None or unary != '-':
        return n
    if isinstance(n, int):
        return int(unary + str(n))
    elif isinstance(n, float):
        return float(unary + str(n))
    else:
        raise ValueError("Unknown unary number", n, unary)

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
        return Name(obj.id)
    elif isinstance(obj, ast.Subscript):
        return extract_subscript(obj)
    else:
        raise ValueError("Unsuported source")

def extract_subscript(obj):
    if not isinstance(obj, ast.Subscript):
        raise ValueError("Object is not subscript")
    path = None
    if isinstance(obj.value, ast.Name):
        name = obj.value.id
    elif isinstance(obj.value, ast.Attribute):
        name, path = extract_path(obj.value)
    else:
        raise ValueError("Not suported name(attribute) in subscript!")
    if isinstance(obj.slice.value, ast.Num):
        index = Const(obj.slice.value.n)
    else:
        raise ValueError("Only constants for now in subscript TODO rest!")
    return Subscript(name, index, path)

def extract_operand(obj):
    if isinstance(obj, ast.UnaryOp):
        if isinstance(obj.operand, ast.Num):
            if isinstance(obj.operand.n, int):
                return Const(int(extract_unary(obj.op) + str(obj.operand.n)))
            elif isinstance(obj.operand.n, float):
                return Const(float(extract_unary(obj.op) + str(obj.operand.n)))
            else:
                raise ValueError('Unsuported constant', obj.operand.n)
        else:
            raise ValueError("Unsuported operand in unary operator", obj.operand)
    if isinstance(obj, ast.Num):
        return Const(obj.n)
    elif isinstance(obj, ast.Name):
        return Name(obj.id)
    elif isinstance(obj, ast.Tuple) or isinstance(obj, ast.List):
        return Const(extract_numbers(obj))
    elif isinstance(obj, ast.Attribute):
        src, src_path = extract_path(obj)
        return Attribute(src, src_path)
    elif isinstance(obj, ast.Subscript):
        return extract_subscript(obj)
    elif isinstance(obj, ast.Call):
        func = obj.func.id
        args = []
        for arg in obj.args:
            op = extract_operand(arg)
            args.append(op)
        return Callable(func, args)
    else:
        raise ValueError("Unsuported operand in binary arithmetic.", obj)

def extract_operands(obj):
    op1 = extract_operand(obj.left)
    op2 = extract_operand(obj.right)
    o = operator(obj.op)
    return (op1, o, op2)

def parse_arithmetic(bin_op, operations):
    left = bin_op.left
    right = bin_op.right
    op = bin_op.op
    if not isinstance(left, ast.BinOp) and not isinstance(right, ast.BinOp):
        op1, o, op2 = extract_operands(bin_op)
        operations.append(Operation(left=op1, operator=o, right=op2))
        return operations
    
    if isinstance(left, ast.BinOp):
        parse_arithmetic(left, operations)
        if isinstance(right, ast.BinOp):
            parse_arithmetic(right, operations)
            operations.append(Operation(left=EmptyOperand, operator=operator(op), right=EmptyOperand))
        else:
            op2 = extract_operand(right)
            operations.append(Operation(left=EmptyOperand, operator=operator(op), right=op2))
        return operations

    if isinstance(right, ast.BinOp):
        parse_arithmetic(right, operations)
        if isinstance(left, ast.BinOp):
            parse_arithmetic(left, operations)
            operations.append(Operation(left=EmptyOperand, operator=operator(op), right=EmptyOperand))
        else:
            op2 = extract_operand(left)
            operations.append(Operation(left=op2, operator=operator(op), right=EmptyOperand))
        return operations


    raise ValueError("Unsuported expression", left, right, op)

def parse_arithmetic_old(bin_op):
    left = bin_op.left
    right = bin_op.right
    op = bin_op.op

    #two operands version
    if not isinstance(left, ast.BinOp) and not isinstance(right, ast.BinOp):
        op1, o, op2 = extract_operands(bin_op)
        return [Operation(left=op1, operator=o, right=op2)]

    #min four operands version
    if isinstance(left, ast.BinOp) and isinstance(right, ast.BinOp):
        ops = []
        op1, o1, op2 = extract_operands(left)
        op3, o2, op4 = extract_operands(right)
        ops.append(Operation(left=op1, operator=o1, right=op2))
        ops.append(Operation(left=op3, operator=o2, right=op4))
        ops.append(Operation(left=EmptyOperand, operator=operator(op), right=EmptyOperand))
        return ops

    # min three operands version
    if isinstance(left, ast.BinOp) or isinstance(right, ast.BinOp):
        ops = []
        if isinstance(left, ast.BinOp):
            if isinstance(left.left, ast.BinOp): #four operands version
                op1, o, op2 = extract_operands(left.left)
                ops.append((op1, o, op2))
                o = operator(left.op)
                op2 = extract_operand(left.right)
                ops.append(Operation(left=EmptyOperand, operator=o, right=op2))
            elif isinstance(left.right, ast.BinOp):
                op1, o, op2 = extract_operands(left.right)
                ops.append((op1, o, op2))
                o = operator(left.op)
                op2 = extract_operand(left.left)
                ops.append(Operation(left=op2, operator=o, right=EmptyOperand))
            else:
                op1, o, op2 = extract_operands(left)
                ops.append(Operation(left=op1, operator=o, right=op2))
        if isinstance(right, ast.BinOp):
            if isinstance(right.left, ast.BinOp): # four operands version
                op1, o, op2 = extract_operands(right.left)
                ops.append(Operation(left=op1, operator=o, right=op2))
                o = operator(right.op)
                op2 = extract_operand(right.right)
                ops.append(Operation(left=EmptyOperand, operator=o, right=op2))
            elif isinstance(right.right, ast.BinOp):
                raise ValueError("Not yet implemented")
            else:
                op1, o, op2 = extract_operands(right)
                ops.append(Operation(left=op1, operator=o, right=op2))

        o = operator(op)
        if not isinstance(left, ast.BinOp):
            op2 = extract_operand(left)
            ops.append(Operation(left=op2, operator=o, right=EmptyOperand))
        if not isinstance(right, ast.BinOp):
            op2 = extract_operand(right)
            ops.append(Operation(left=EmptyOperand, operator=o, right=op2))
        return ops
    raise ValueError("Two complex expression")

def extract_con_op(obj):
    if isinstance(obj, ast.Lt):
        return '<'
    elif isinstance(obj, ast.Gt):
        return '>'
    elif isinstance(obj, ast.Eq):
        return '=='
    elif isinstance(obj, ast.LtE):
        return '<='
    elif isinstance(obj, ast.GtE):
        return '>='
    elif isinstance(obj, ast.NotEq):
        return '!='
    else:
        raise ValueError("Unknown conditions operator", obj)

def extract_test(obj):
    if isinstance(obj, ast.Num):
        test = ((Const(obj.n),),)
    elif isinstance(obj, ast.Name):
        test = ((Name(obj.id),),)
    elif isinstance(obj, ast.Attribute):
        name, path = extract_path(obj)
        test = ((Attribute(name, path),),)
    elif isinstance(obj, ast.Compare):
        if len(obj.comparators) != 1:
            raise ValueError("Not suported yet comparators", obj.comparators)
        left_op = extract_operand(obj.left)
        right_op = extract_operand(obj.comparators[0])
        if len(obj.ops) != 1:
            raise ValueError("Not suported yet multiple conditions operators", obj.ops)
        con = extract_con_op(obj.ops[0])
        test = ((left_op, con, right_op),)
    else: 
        raise ValueError("Unknown test!", obj)
    return test

class Parser:
    def __init__(self):
        pass

    def _simple_assigments(self, targets, obj, unary=None):
        op = extract_operand(obj)
        if unary is not None and isinstance(op, Const):
            op.const = unary_number(op.const, unary)
            unary = None
        for t in targets:
            if isinstance(t, (ast.Attribute, ast.Name, ast.Subscript)):
                return StmAssign(make_name(t), op, unary)
            else:
                raise ValueError("Unknown target", t)

    def _binary_operation(self, targets, obj, unary=None):
        expr = parse_arithmetic(obj, [])
        for t in targets:
            if isinstance(t, (ast.Attribute, ast.Name, ast.Subscript)):
                return StmAssign(make_name(t), Operations(expr), unary)
            else:
                raise ValueError("Unknown target", t)

    def _parse_assign(self, assign):
        if isinstance(assign.value, ast.Num):
            return self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Name):
            return self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.BinOp):
            return self._binary_operation(assign.targets, assign.value)
        elif isinstance(assign.value, ast.UnaryOp):
            op = extract_unary(assign.value.op)
            if isinstance(assign.value.operand, ast.BinOp):
                return self._binary_operation(assign.targets, assign.value.operand, op)
            else:
                return self._simple_assigments(assign.targets, assign.value.operand, op)
        elif isinstance(assign.value, ast.Call):
            return self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Subscript):
            return self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Tuple):
            return self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.List):
            return self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.Attribute):
            return self._simple_assigments(assign.targets, assign.value)
        else:
            raise ValueError("Unknown assign", assign.value)

    def _parse_call(self, call):
        if isinstance(call.func, ast.Name):
            func = call.func.id
        elif isinstance(call.func, ast.Attribute):
            raise ValueError('Classes are not yet implemented!!!')
        else:
            raise ValueError("Unsuported function call", call.func)
        args = []
        for arg in call.args:
            op = extract_operand(arg)
            args.append(op)
        return StmExpression(Callable(func, args))

    def _parse_return(self, obj):
        src = extract_operand(obj)
        return StmReturn(src)

        if isinstance(obj, ast.Num):
            return StmReturn(cgen, const=obj.n)
        elif isinstance(obj, ast.Name):
            return StmReturn(cgen, src=obj.id)
        elif isinstance(obj, ast.Attribute):
            name, path = extract_path(t)
            return StmReturn(src=Attribute(name, path))
        elif obj is None: #empty return statement
            return StmReturn()
        else:
            raise ValueError("Unknown return object", obj)

    def _parse_if(self, obj, br_label):
        test = extract_test(obj.test)
        body = []
        for statement in obj.body:
            stm = self._parse_statement(statement, br_label)
            body.append(stm)
        if not obj.orelse:
            stm_if = StmIf(body, test)
            return stm_if
        else:
            if isinstance(obj.orelse[0], ast.If):
                raise ValueError("if test: elif test ...., not implemented yet")
            orelse_body = []
            for statement in obj.orelse:
                stm = self._parse_statement(statement, br_label)
                orelse_body.append(stm)
            stm_if = StmIf(body, test, orelse_body)
            return stm_if

        raise ValueError("Not yet implemented this version of If statement", obj)

    def _parse_while(self, obj):
        if obj.orelse:
            raise ValueError("Orelse in while still not suported")
        test = extract_test(obj.test)
        body = []
        stm_while = StmWhile(body, test)
        for statement in obj.body:
            stm = self._parse_statement(statement, stm_while.label())
            body.append(stm)
        return stm_while

    def _parse_statement(self, statement, br_label=None):
        if isinstance(statement, ast.Assign):
            return self._parse_assign(statement)
        elif isinstance(statement, ast.For):
            raise ValueError('For statement', statement)
        elif isinstance(statement, ast.While):
            return self._parse_while(statement)
        elif isinstance(statement, ast.Pass):
            raise ValueError('Pass statement', statement)
        elif isinstance(statement, ast.Expr):
            if isinstance(statement.value, ast.Call): # function call
                return self._parse_call(statement.value)
            else:
                raise ValueError('Expr statement', statement, statement.value)
        elif isinstance(statement, ast.If):
            return self._parse_if(statement, br_label)
        elif isinstance(statement, ast.Return):
            return self._parse_return(statement.value)
        elif isinstance(statement, ast.Break):
            return StmBreak(br_label)
        else:
            raise ValueError('Uknown satement', statement)

    def parse(self, source, cgen):
        code = ast.parse(source)

        if isinstance(code, ast.Module):
            for statement in code.body:
                stm = self._parse_statement(statement)
                cgen.add(stm)
        else:
            raise ValueError('Source is not instance of ast.Module', code)

        return cgen


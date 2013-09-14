
"""
    This module implement parser for shading language that create
    list of statements from source.
"""

import ast
from .stms import StmIf, StmWhile, StmBreak, StmAssign, StmReturn, StmExpression, StmEmpty

class Attribute:
    """
        Class represents attribute(filed) in structure.
    """
    def __init__(self, name, path):
        self.name = name #name of struct
        self.path = path #path to member in struct

class Callable:
    """
        Class represents function in shading language.
    """
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Const:
    """
        Class represents constant(int, float).
        Also const can hold tuple of constants.
    """
    def __init__(self, const):
        self.const = const

class Name:
    """
        Class represents name(variable) in shading language.
    """
    def __init__(self, name):
        self.name = name

class Subscript:
    """
        Class represents item in array.
    """
    def __init__(self, name, index, path=None):
        self.name = name
        self.index = index
        #if we have path than this is array in struct
        self.path = path #path to member in struct

class NoOp:
    """
        In arithmetic, with this class we indicate that we are
        missing left or right operand.
    """
    pass

class Operation:
    """
        Class that represent simple arithmetic operation.
    """
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Operations:
    """
       Class that holds list of arithmetic operations. 
    """
    def __init__(self, operations):
        self.operations = operations


def operator(obj):
    """
       Extract arithmetic operator from ast object. 
    """
    o = {ast.Add:'+', ast.Mult:'*', ast.Sub:'-', ast.Div:'/', ast.Mod:'%'}
    return o[type(obj)]

def extract_unary(obj):
    """
       Extract unary operator from ast object. 
    """
    o = {ast.USub:'-', ast.UAdd:'+'}
    return o[type(obj)]


def extract_numbers(obj):
    """
        Return tuple of constants from ast.Tuple, ast.List object 
    """
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
    return tuple(numbers)

def extract_path(obj):
    """
        Construct path from ast.Attribute object
    """
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

def unary_number(obj):
    if isinstance(obj.operand, ast.Num):
        if isinstance(obj.operand.n, int):
            return Const(int(extract_unary(obj.op) + str(obj.operand.n)))
        elif isinstance(obj.operand.n, float):
            return Const(float(extract_unary(obj.op) + str(obj.operand.n)))
        else:
            raise ValueError('Unsuported constant', obj.operand.n)
    else:
        raise ValueError("Unsuported operand in unary operator", obj.operand)


def extract_operand(obj):
    if isinstance(obj, ast.UnaryOp):
        return unary_number(obj)
    if isinstance(obj, ast.Num):
        return Const(obj.n)
    elif isinstance(obj, ast.Name):
        return Name(obj.id)
    elif isinstance(obj, (ast.Tuple, ast.List)):
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


def parse_arithmetic(bin_op, operations):
    """
        Flaten arithmetic expression in array of simple
        arithmetic operations.
    """
    left = bin_op.left
    right = bin_op.right
    op = bin_op.op
    if not isinstance(left, ast.BinOp) and not isinstance(right, ast.BinOp):
        op1 = extract_operand(bin_op.left)
        op2 = extract_operand(bin_op.right)
        o = operator(bin_op.op)
        operations.append(Operation(left=op1, operator=o, right=op2))
        return operations
    
    if isinstance(left, ast.BinOp):
        parse_arithmetic(left, operations)
        if isinstance(right, ast.BinOp):
            parse_arithmetic(right, operations)
            operations.append(Operation(left=NoOp, operator=operator(op), right=NoOp))
        else:
            op2 = extract_operand(right)
            operations.append(Operation(left=NoOp, operator=operator(op), right=op2))
        return operations

    if isinstance(right, ast.BinOp):
        parse_arithmetic(right, operations)
        if isinstance(left, ast.BinOp):
            parse_arithmetic(left, operations)
            operations.append(Operation(left=NoOp, operator=operator(op), right=NoOp))
        else:
            op2 = extract_operand(left)
            operations.append(Operation(left=op2, operator=operator(op), right=NoOp))
        return operations

    raise ValueError("Unsuported expression", left, right, op)


def extract_con_op(obj):
    """
       Extract conditional operator from ast object. 
    """
    o = {ast.Lt:'<', ast.Gt:'>', ast.Eq:'==', ast.LtE:'<=', ast.GtE:'>=', ast.NotEq:'!='}
    return o[type(obj)]


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


def parse_assign(assign):
    if len(assign.targets) > 1:
        raise ValueError("Only one target is supported for now.")
    if isinstance(assign.value, ast.BinOp):
        expr = parse_arithmetic(assign.value, [])
        ops = Operations(expr)
    else:
        ops = extract_operand(assign.value)

    for t in assign.targets: 
        return StmAssign(make_name(t), ops)


def parse_call(call):
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


def parse_return(obj):
    src = extract_operand(obj)
    return StmReturn(src)

def parse_if(obj, br_label):
    test = extract_test(obj.test)
    body = []
    for statement in obj.body:
        stm = parse_statement(statement, br_label)
        body.append(stm)
    if not obj.orelse:
        stm_if = StmIf(body, test)
        return stm_if
    else:
        if isinstance(obj.orelse[0], ast.If):
            raise ValueError("if test: elif test ...., not implemented yet")
        orelse_body = []
        for statement in obj.orelse:
            stm = parse_statement(statement, br_label)
            orelse_body.append(stm)
        stm_if = StmIf(body, test, orelse_body)
        return stm_if

    raise ValueError("Not yet implemented this version of If statement", obj)

def parse_while(obj):
    if obj.orelse:
        raise ValueError("Orelse in while still not suported")
    test = extract_test(obj.test)
    body = []
    stm_while = StmWhile(body, test)
    for statement in obj.body:
        stm = parse_statement(statement, stm_while.label())
        body.append(stm)
    return stm_while

def parse_statement(statement, br_label=None):
    if isinstance(statement, ast.Assign):
        return parse_assign(statement)
    elif isinstance(statement, ast.For):
        raise ValueError('For statement is not supported', statement)
    elif isinstance(statement, ast.While):
        return parse_while(statement)
    elif isinstance(statement, ast.Pass):
        return StmEmpty()
    elif isinstance(statement, ast.Expr):
        if isinstance(statement.value, ast.Call): # function call
            return parse_call(statement.value)
        else:
            raise ValueError('Expr statement', statement, statement.value)
    elif isinstance(statement, ast.If):
        return parse_if(statement, br_label)
    elif isinstance(statement, ast.Return):
        return parse_return(statement.value)
    elif isinstance(statement, ast.Break):
        return StmBreak(br_label)
    else:
        raise ValueError('Uknown satement', statement)

def parse(text):
    """
        Parse source(shading language source) and return
        list of statements.
        For parsing is used ast module which means that
        syntax of python and shading lanugage is identical.
    """
    code = ast.parse(text)

    if not isinstance(code, ast.Module):
        raise ValueError('Source is not instance of ast.Module', code)

    stms = [parse_statement(stm) for stm in code.body]
    return stms


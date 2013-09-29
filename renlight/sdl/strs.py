
class Attribute:
    """
        Class represents attribute(filed) in structure.
    """
    def __init__(self, name, path):
        self.name = name  # name of struct
        self.path = path  # path to member in struct


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
        self.path = path  # path to member in struct


class NoOp:
    """
        In arithmetic and conditions, with this class we indicate that we are
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


class Condition:
    """
       Class that one simple logic condition
    """
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Conditions:
    """
       Class that holds list of logic conditions.
    """
    def __init__(self, conditions, logic_ops):
        assert len(conditions) == len(logic_ops) + 1
        self.conditions = conditions
        self.logic_ops = logic_ops

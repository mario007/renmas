
import ast

class Generator:
    def __init__(self):
        pass

    def _clear(self):
        self._data_section = "#DATA\n"
        self._code_section = "#CODE\n"
        pass

    def _add_param_to_ds(self, param):
        pass

    def _add_code(self, code):
        pass

    def _simple_assigments(self, targets, obj):
        if isinstance(obj, ast.Num):
            n = obj.n
            if isinstance(n, int):
                print('Simple integer assigments')
            elif isinstance(n, float):
                print('Simple float assigments')
            else:
                print('Unknown number type', type(n))
        elif isinstance(obj, ast.Name):
            print('Simple name assigments')
        else:
            print ('Unknown', obj)
        print (targets)

    def _bin_operation(self, targets, bin_op):
        left = bin_op.left
        op = bin_op.op
        right = bin_op.right
        if isinstance(op, ast.Add):
            operator = '+'
        elif isinstance(op, ast.Mult):
            operator = '*'
        elif isinstance(op, ast.Div):
            operator = '/'
        elif isinstance(op, ast.Sub):
            operator = '-'
        else:
            raise ValueError('Unknown binary operation', op)
        if isinstance(left, ast.Name):
            print ('Left', left.id)
        elif isinstance(left, ast.Num):
            print ('Left', left.n)

        if isinstance(right, ast.Name):
            print ('Right', right.id)
        elif isinstance(right, ast.Num):
            print ('Right', right.n)

    def _assign(self, assign):
        if isinstance(assign.value, ast.Num) or isinstance(assign.value, ast.Name):
            self._simple_assigments(assign.targets, assign.value)
        elif isinstance(assign.value, ast.BinOp):
            self._bin_operation(assign.targets, assign.value)
        elif isinstance(assign.value, ast.UnaryOp):
            print ('Unary operator')
        else:
            print('Unknown assign', assign.value)

    def _statement(self, statement):
        if isinstance(statement, ast.Assign):
            self._assign(statement)
        else:
            raise ValueError('Uknown satement', statement)

    def generate(self, code):
        self._clear()
        if not isinstance(code, ast.Module):
            return None

        for statement in code.body:
            self._statement(statement)

        return self._data_section + self._code_section

def generate_code(source):
    code = ast.parse(source)
    if isinstance(code, ast.Module):
        gen = Generator()
        return gen.generate(code)
    else:
        raise ValueError('')

source = "g = 3"
print(generate_code(source))


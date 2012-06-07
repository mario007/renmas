from .shader import Shader, Param, Statement, LocalVar

class OSLParser:
    def __init__(self):
        self._data_types = ['int', 'float', 'point', 'vector', 'normal', 'color', 'matrix', 'string']
        self._shader_types = ('surface', 'displacement', 'light', 'volume', 'shader')
        self._functions = {}

    def parse(self, tokens):
        self._tokens = tokens

        self._params = {} 
        self._constants = {} 
        self._locals = {}

        self._statements = []
        
        self._parse_shader()

        return Shader(self._shader_name, self._shader_type, self._params, self._statements, self._locals)

    def _parse_shader(self):
        token = self._next('iden')
        if token is None: raise ValueError("Wrong shader type!!!")
        tk_typ, tk_value, line = token
        if tk_value not in self._shader_types:
            raise ValueError("Optinal functions and structures are not yet supported.")
        self._shader_type = tk_value
        token = self._next('iden')
        if token is None: raise ValueError("Wrong shader name!!!")
        tk_typ, tk_value, line = token
        self._shader_name = tk_value
        token = self._next('special', '(')
        if token is None: raise ValueError("Missing '(' in shader declaration")
        token = self._next2([('keyword', None), ('special', ')')])
        if token is None: raise ValueError("Missing ')' in shader declaration")
        tk_typ, tk_value, line = token
        if tk_typ == 'keyword':
            self._parse_parameters(token)
        token = self._next('special', '{')
        if token is None: raise ValueError("Missing '{' in shader declaration")

        #TODO - think ';' - empty statements
        token = self._next2([('special', '}'), ('iden', None), ('keyword', None)])
        if token is None: raise ValueError("Missing '}' in shader declaration")
        tk_typ, tk_value, line = token
        if tk_value == '}':
            # check if this is end of shader!!! TODO
            return

        self._parse_statements(token)
        # check if this is end of shader!!! TODO

    def _parse_parameters(self, token):
        while True:
            ret = self._parse_parameter(token)
            if ret is not True: return # no more parameters
            token = self._next('keyword', None)
            if token is None: raise ValueError("Missing keyword after ',' in paramters")

    def _parse_parameter(self, token):
        tk_typ, tk_value, line = token
        output = False
        val = None
        if tk_value == 'output':
            token = self._next('keyword', None)
            if token is None: raise ValueError("Missing data type after keyword output", token)
            tk_typ, tk_value, line = token
            output = True

        if tk_typ == 'keyword' and tk_value in self._data_types:
            data_type = tk_value
        else:
            raise ValueError("Wrong data type!!!", token)
        token = self._next('iden')
        if token is None: raise ValueError("Missing name for parameter")
        tk_typ, tk_value, line = token
        if tk_value in self._params:
            raise ValueError("Parameter with that name allready exist!", token)
        param_name = tk_value
        token = self._next2([('special', ')'), ('comma', None), ('operators', '=')])
        if token is None: raise ValueError("Syntax Error in params. '=', ',', ')' is expected.")
        tk_typ, tk_value, line = token
        if tk_value == ')':
            self._create_param(param_name, data_type, val, output)
            return False
        elif tk_typ == 'comma':
            self._create_param(param_name, data_type, val, output)
            return True
        elif tk_value == '=':
            # TODO -- parse expression
            raise ValueError("Expression parssing is not yet implemented.")
        else:
            raise ValueError("Syntax error in parameter parsing", token)

    def _parse_statements(self, token):
        while True:
            self._parse_statement(token)
            token = self._next2([('keyword', None), ('special', '}'), ('iden', None)])
            if token is None: raise ValueError("Syntax error in parse statements")
            tk_typ, tk_value, line = token
            if tk_value == '}': return

    def _parse_statement(self, token):
        tk_typ, tk_value, line = token
        if tk_typ == 'keyword':
            if tk_value in self._data_types:
                typ = tk_value
                token = self._next('iden')
                if token is None: raise ValueError("Identifier expected.")
                tk_typ, tk_value, line = token
                name = tk_value
                token = self._next2([('special', ';'), ('comma', None), ('operators', '=')])
                if token is None: raise ValueError("Missing ; for end of statement")
                tk_typ, tk_value, line = token
                self._create_local_var(name, typ)
                if tk_value == ';': return
                elif tk_value == ',':
                    while True:
                        token = self._next('iden')
                        if token is None: raise ValueError("Identifier expected.")
                        tk_typ, tk_value, line = token
                        self._create_local_var(tk_value, typ)
                        token = self._next2([('special', ';'), ('comma', None)])
                        if token is None: raise ValueError("Comma or ';' is expected.")
                        tk_typ, tk_value, line = token
                        if tk_value == ';': return 
                        elif tk_value == ',': continue
                        else: raise ValueError("Unexpected token in parse statement", token)
                elif tk_value == '=':
                    self._parse_expression(typ, name)
            elif tk_value in ('for', 'while', 'if', 'do'):
                raise ValueError("For ,while, if and do are not yet implemented.")
            else:
                raise ValueError("Not implemented or not supported keyword")
        elif tk_typ == 'iden':
            typ = self._iden_type(tk_value)
            if typ is None: raise ValueError("Identifier %s doesn't have type or doesn't exist!" % tk_value)
            token = self._next('operators', '=')
            if token is None: raise ValueError("Missing operator '='")
            self._parse_expression(typ, tk_value)
            return
        else:
            raise ValueError('Syntax error in Statement', token)

    def _parse_expression(self, typ, name):
        idens = []
        operators = []
        statement_type = typ 

        if self._readonly(name): raise ValueError("Identifier '" + tk_value + "' is readonly!")
        assign_iden = name 
        token = self._next2([('iden', None), ('number', None), ('decimal', None)])
        if token is None: raise ValueError("Missing identifier or constant number!!!")
        tk_typ, tk_value, line = token
        
        if tk_typ == "number" or tk_typ == "decimal":
            pass # TODO process constant
            raise ValueError("Process constant!")
        elif self._is_function(tk_value):
            pass # TODO process function call
            raise ValueError("Function call yot net implemented.")

        if statement_type != self._iden_type(tk_value):
            raise ValueError("Types od identifiers '" + assign_iden + "' and '" + tk_value + "' doesn't match!") 

        #TODO binary operations and function calls
        token = self._next('special', ';')
        if token is None: raise ValueError("Missing ';' for end of statement.")

        #TODO -- generate code
        code = self._generate_assign(assign_iden, tk_value, statement_type)
        self._statements.append(Statement(code))
        return

    def _next(self, typ, value=None, space=True):

        while True:
            try:
                token = next(self._tokens)
            except StopIteration:
                raise ValueError("Unexpected end of shader!", token)

            tk_typ, tk_value, line = token
            if tk_typ == 'comment' or tk_typ == 'multi_comment':
                continue
            if space:
                if tk_typ == "new_line" or tk_typ == "space":
                    continue
            
            if value is not None:
                if typ == tk_typ and value == tk_value:
                    return (tk_typ, tk_value, line)
                else:
                    return None
            else:
                if typ == tk_typ:
                    return (tk_typ, tk_value, line)
                else:
                    return None


    def _next2(self, typ_vals, space=True):

        while True:
            try:
                token = next(self._tokens)
            except StopIteration:
                raise ValueError("Unexpected end of shader!", token)

            tk_typ, tk_value, line = token
            if tk_typ == 'comment' or tk_typ == 'multi_comment':
                continue
            if space:
                if tk_typ == "new_line" or tk_typ == "space":
                    continue

            for typ, value in typ_vals:
                if value is not None:
                    if typ == tk_typ and value == tk_value:
                        return (tk_typ, tk_value, line)
                else:
                    if typ == tk_typ:
                        return (tk_typ, tk_value, line)
            else:
                return None

    def _create_constant(self, typ, value):
        pass

    def _get_constant(self, name, value):
        pass

    def _iden_exist(self, name):
        if name in self._params:
            return True
        if name in self._constants:
            return True
        if name in self._locals:
            return True
        if name in self._functions:
            return True
        return False

    def _iden_type(self, name):
        if name in self._params:
            return self._params[name].typ
        if name in self._constants:
            return self._constants[name].typ
        if name in self._locals:
            return self._locals[name].typ
        return None 
    
    def _check_types(self, name1, name2):
        if not self._iden_exist(name1): return False
        if not self._iden_exist(name2): return False
        return self._iden_type(name1) == self._iden_type(name2)
    
    def _readonly(self, name):
        if name in self._params:
            return not self._params[name].output
        return False

    def _is_function(self, name):
        return False 

    def _generate_assign(self, iden1, iden2, typ):
        if typ == "float":
            return "macro eq32 " + iden1 + " = " + iden2 + " {xmm7}"
        elif typ == "vector":
            return "macro eq128 " + iden1 + " = " + iden2 + " {xmm7}" 
        else:
            raise ValueError("Type " + typ + " is not yet supported!")
    
    def _create_local_var(self, name, typ, val=None):
        if self._iden_exist(name):
            raise ValueError("Identifier %s allready exist" % name)
        v = LocalVar(name, typ, val)
        self._locals[name] = v
        return v

    def _create_param(self, name, typ, val, output):
        if self._iden_exist(name):
            raise ValueError("Identifier %s allready exist" % name)
        self._params[name] = Param(name, typ, val, output)


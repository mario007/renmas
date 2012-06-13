import platform
from .shader import Shader, Param, Statement, LocalVar, Constant
#TODO -- normal, ... can't be name of variables

def _reg_struct_members(members):
    # hit is actualy point type TODO
    members['hitpoint.hit'] = 'vector'
    #members['hitpoint.normal'] = 'vector'
    members['hitpoint.t'] = 'float'

class OSLParser:
    def __init__(self):
        self._data_types = ['void', 'int', 'float', 'point', 'vector', 'normal', 'color', 'matrix', 'string']
        self._shader_types = ('surface', 'displacement', 'light', 'volume', 'shader')
        self._functions = {}
        self._structures = {'hitpoint':'hitpoint'}

    def parse(self, tokens):
        self._struct_members = {}
        _reg_struct_members(self._struct_members)

        self._tokens = tokens
        
        self._idx_con = 0

        self._params = {} 
        self._param_list = []
        self._constants = {} 
        self._contypvalue = {} 
        self._locals = {}
        self._statements = []
        
        self._parse_shader()
        return Shader(self._shader_name, self._shader_type, self._param_list,
                self._statements, self._locals, self._constants)

    def _parse_shader(self):
        token = self._next2([('iden', None), ('keyword', None)])
        if token is None: raise ValueError('Syntax error at begining of shader!')
        tk_typ, tk_value, line = token
        if tk_typ == 'iden':
            if tk_value not in self._shader_types: raise ValueError('Wrong shader type %s!' % tk_value)
            self._shader_type = tk_value
        else:#keyword token
            if tk_value == 'struct': self._parse_struct()
            elif tk_value in self._data_types: self._parse_function(tk_value)
            else: raise ValueError('Wrong keyword "%s" at begining of shader!' % tk_value)

        token = self._next('iden')
        if token is None: raise ValueError("Wrong shader name!!!")
        tk_typ, tk_value, line = token
        self._shader_name = tk_value
        #TODO - Check if shader name is legal! different from constants, functions etc...!

        token = self._next('special')
        if token is None: raise ValueError('Syntax error "(" is expected.')
        tk_typ, tk_value, line = token
        if tk_value == '[': self._parse_metadata()
        elif tk_value != '(': raise ValueError('Syntax error "(" is expected.')
        
        self._parse_parameters()

        token = self._next('special', '{')
        if token is None: raise ValueError("Missing '{' in shader declaration")

        self._parse_statements()
        # check if this is end of shader!!! TODO

    def _parse_parameters(self):
        token = self._next2([('keyword', None), ('special', ')'), ('iden', None)])
        if token is None: raise ValueError("Missing ')' in shader parametars declaration")
        tk_typ, tk_value, line = token
        if tk_value == ')': return #shader have no parametars

        while True:
            ret = self._parse_parameter(token)
            if ret is not True: return # no more parameters
            token = self._next2([('keyword', None), ('iden', None)])
            if token is None: raise ValueError("Missing keyword after ',' in paramters")

    def _parse_parameter(self, token):
        tk_typ, tk_value, line = token
        output = False
        val = None
        if tk_value == 'output':
            token = self._next2([('keyword', None), ('iden', None)])
            if token is None: raise ValueError("Missing data type after keyword output", token)
            tk_typ, tk_value, line = token
            output = True

        if tk_typ == 'keyword' and tk_value in self._data_types: 
            data_type = tk_value
        elif tk_typ == 'iden' and tk_value in self._structures:
            data_type = tk_value
        else:
            raise ValueError("Wrong data type!!!", token)

        token = self._next('iden')
        if token is None: raise ValueError("Missing name for parameter")
        tk_typ, tk_value, line = token
        if tk_value in self._params:
            raise ValueError("Parameter with that name allready exist!", token)
        param_name = tk_value

        token = self._next2([('special', ')'), ('comma', None), ('special', '['),('operators', '=')])
        if token is None: raise ValueError("Syntax Error in params. '=', ',',')' or '[' is expected.")
        tk_typ, tk_value, line = token
        if tk_value == ')':
            self._create_param(param_name, data_type, val, output)
            return False
        elif tk_typ == 'comma':
            self._create_param(param_name, data_type, val, output)
            return True
        elif tk_value == '[':
            raise ValueError('Array parameter is not yet supported.')
        elif tk_value == '=':
            # TODO -- parse expression
            raise ValueError("Constant expression parssing in shader param is not yet implemented.")
        else:
            raise ValueError("Syntax error in parameter parsing", token)

    def _parse_statements(self):
        token = self._next2([('special', '}'), ('iden', None), ('keyword', None), ('special', ';')])
        if token is None: raise ValueError("Missing '}' in shader declaration")
        tk_typ, tk_value, line = token
        if tk_value == '}': return

        while True:
            self._parse_statement(token)
            token = self._next2([('keyword', None), ('special', '}'), ('iden', None), ('special', ';')])
            if token is None: raise ValueError("Syntax error in parse statements")
            tk_typ, tk_value, line = token
            if tk_value == '}': return

    def _parse_statement(self, token):
        tk_typ, tk_value, line = token
        if tk_typ == 'keyword' or tk_typ == 'iden':
            if tk_value in ('for', 'while', 'if', 'do'):
                self._parse_loop()
            if tk_value in self._data_types or tk_value in self._structures:
                typ = tk_value
                token = self._next('iden')
                if token is None: raise ValueError("Identifier expected.")
                tk_typ, tk_value, line = token
                name = tk_value
                token = self._next2([('special', ';'), ('comma', None), ('operators', '=')])
                if token is None: raise ValueError("Missing ; for end of statement")
                self._create_local_var(name, typ)
                tk_typ, tk_value, line = token
                if tk_value == ';': return
                elif tk_value == ',':
                    self._multiple_variables(typ)
                elif tk_value == '=':
                    self._parse_arithmetic(typ, name)
            else:
                name = tk_value
                typ = self._iden_type(tk_value)
                if typ is None: raise ValueError("Identifier %s doesn't have type or doesn't exist!" % tk_value)
                token = self._next2([('operators', '='), ('special', '.')])
                if token is None: raise ValueError("Missing operator '='")
                tk_typ, tk_value, line = token
                if tk_value == '=':
                    self._parse_arithmetic(typ, name)
                elif tk_value == '.':
                    full_name = name
                    while True:
                        token = self._next('iden')
                        if token is None: raise ValueError('Missing identifier in statement.', token)
                        tk_typ, tk_value, line = token
                        full_name += "." + tk_value
                        token = self._next2([('operators', '='), ('special', '.')])
                        if token is None: raise ValueError('Missing operator = in statement.', token)
                        tk_typ, tk_value, line = token
                        if tk_value == '=': break
                        elif tk_value == '.': continue
                        else: raise ValueError('Syntax error in statement.')
                    typ = self._member_type(full_name)
                    self._parse_arithmetic(typ, full_name)
                else:
                    raise ValueError('Syntax error in Statement', token)

        elif tk_typ == 'special' and tk_value == ';': #empty statement
            return
        else:
            raise ValueError('Syntax error in Statement', token)

    def _multiple_variables(self, typ):
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
    
    def _parse_member(self, typ):

        token = self._next2([('iden', None), ('number', None), ('decimal', None)])
        if token is None: raise ValueError("Missing identifier or constant number!!!")
        tk_typ, tk_value, line = token
        if tk_typ == "number" or tk_typ == "decimal":
            #TODO - vector constants or others besides floats
            con = self._fetch_const(typ, tk_value)
            op_name = con.name
        elif self._is_function(tk_value):
            #TODO -- process function call and put result to some temp variable
            raise ValueError("Built in functions call yot net implemented.")
        else:
            if not self._iden_exist(tk_value): raise ValueError("Identifier %s doesn't exist" % tk_value)
            if not self._is_structure(tk_value):
                op_name = tk_value
            else:
                raise ValueError('Not yet arithmetic structure')
        return op_name

    def _parse_arithmetic(self, typ, name):
        #TODO -- readonly sctructure member
        if self._readonly(name): raise ValueError("Identifier %s is readonly!" % name)
        
        s_to_reg = ""
        mem_type = self._member_type(name)
        if mem_type is not None:
            c = name.index('.')
            n = name[0:c]
            t = self._iden_type(n)
            bits = platform.architecture()[0]
            name = 'eax.' + t + name[c:]
            if bits == "64bit":
                s_to_reg = "mov rax, %s \n" % n
            else:
                s_to_reg = "mov eax, %s \n" % n

        if typ == 'float':
            code = 'macro eq32 %s = ' % name
        elif typ == 'vector':
            code = 'macro eq128 %s = ' % name
        else:
            raise ValueError('Not yet supported int expressions or others!')
        
        op_name = self._parse_member(typ)
        reg = " {xmm7}"
        typ1 = self._iden_type(op_name)

        token = self._next2([('special', ';'), ('operators', None)])
        if token is None: raise ValueError("Missing ';' for end of statement.")
        tk_typ, tk_value, line = token
        if tk_typ == 'operators' and tk_value in ('+', '-', '/', '*'):
            op = tk_value
            op_name2 = self._parse_member(typ)
            typ2 = self._iden_type(op_name2)

            # implicit conversion code if needed for some types
            # currently we only have float to vector for multiplication!!!!!
            conv_code = ""
            if op == '*' and typ1 == 'vector' and typ2 == 'float':
                conv_code = "macro eq32 xmm6 = %s \n" % op_name2
                conv_code += "macro broadcast xmm6 = xmm6[0] \n"
                op_name2 = "xmm6"
                typ2 = 'vector'
            elif op== '*' and typ1 == 'float' and typ2 == 'vector':
                conv_code = "macro eq32 xmm6 = %s \n" % op_name
                conv_code += "macro broadcast xmm6 = xmm6[0] \n"
                op_name = "xmm6"
                typ1 = 'vector'
            elif typ != self._iden_type(op_name2):
                raise ValueError("Types mismatch! %s" % op_name2) 

            token = self._next('special', ';')
            if token is None: raise ValueError("Missing ';' for end of statement.")
            if typ != typ1 or typ != typ2:
                raise ValueError("Types mismatch! %s" % op_name2) 
            code += op_name + op + op_name2 + reg
            self._statements.append(Statement(s_to_reg + conv_code + code))
        elif tk_value == ';':
            if typ != self._iden_type(op_name):
                raise ValueError("Types mismatch! %s" % op_name) 
            code += op_name + reg
            self._statements.append(Statement(s_to_reg + code))
        else:
            raise ValueError("unsuported operator in expression", token)

        return
        
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
    
    def _parse_struct(self):
        raise ValueError('User structures are not yet implemented!')
    
    def _parse_function(self, ret_typ):
        raise ValueError('User functions are not yet implemented!')
    
    def _parse_metadata(self):
        raise ValueError('Metadata is not yet implemented!')

    def _parse_loop(self):
        raise ValueError('Looping and "if" is not yet implemented!')

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
    
    def _is_structure(self, name):
        typ = self._iden_type(name)
        if typ is None: return False
        if typ not in self._data_types: return True
        return False

    def _is_leaf(self, name):
        try:
            c = name.index('.')
            n = name[0:c]
            typ = self._iden_type(n)
            full_name = typ + name[c:]
            return full_name in self._struct_members
        except ValueError:
            return False

    def _member_type(self, name):
        try:
            c = name.index('.')
            n = name[0:c]
            typ = self._iden_type(n)
            full_name = typ + name[c:]
            if full_name in self._struct_members:
                return self._struct_members[full_name]
            else:
                return None
        except ValueError:
            return None 
    
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

    def _fetch_const(self, typ, value):
        try:
            c = self._contypvalue[(typ, value)] 
            return c
        except:
            name = self._gen_con_name()
            c = Constant(name , typ, value)
            self._constants[name] = c
            self._contypvalue[(typ, value)] = c
            return c

    def _create_param(self, name, typ, val, output):
        if self._iden_exist(name):
            raise ValueError("Identifier %s allready exist" % name)

        p = Param(name, typ, val, output)
        self._params[name] = p 
        self._param_list.append(p)
    
    def _gen_con_name(self):
        self._idx_con += 1
        return "__con" + str(self._idx_con)  


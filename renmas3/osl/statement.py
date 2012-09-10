import struct
from .arg import  IntArg, FloatArg, Vector3Arg

def float2hex(f):
    r = struct.pack('f', f)
    r1 = struct.unpack('I', r)[0]
    return hex(r1)

def is_num(obj):
    return isinstance(obj, int) or isinstance(obj, float)

def preform_arithmetic(n1, n2, op):
    if op == '+':
        return n1 + n2 
    elif op == '-':
        return n1 - n2
    elif op == '*':
        return n1 * n2
    elif op == '/':
        return n1 / n2
    elif op == '%':
        return n1 % n2
    else:
        raise ValueError("Unknown operator", op)

class Statement:
    def __init__(self):
        pass
    
    def asm_code(self):
        raise NotImplementedError()

#allowed a = b  a, b = spectrums
#allowed a -- vector3, vector4, vector2, float, int
#allowed b -- vector3, vector4, vector2, float, int
#implict conversion just int to float

class StmAssignName(Statement):
    def __init__(self, cgen, dest, src):
        self.cgen = cgen
        self.dest = dest
        self.src = src

    def asm_code(self):
        #asm code depentd type of name1 and name2
        # name can be integer, vector, float etc...
        # implicit conversions int to float etc...
        typ_src = self.cgen.type_of(self.src)
        if typ_src is None: #source doesn't exist
            raise ValueError('Source doesnt exist', self.src)
        typ_dst = self.cgen.type_of(self.dest)
        if typ_dst is None: #create local for destination
            self.cgen.create_local(self.dest, self.src)
            typ_dst = self.cgen.type_of(self.dest)

        if typ_src != typ_dst: # TODO implict conversion
            raise ValueError('Type mismatch', typ_dst, typ_src)

        if typ_src == IntArg and typ_dst == IntArg:
            reg = self.cgen.fetch_register('general')
            line1 = "mov %s, dword [%s] \n" % (reg, self.src)
            line2 = "mov dword [%s], %s \n" % (self.dest, reg)
            return line1 + line2
        elif typ_src == FloatArg and typ_dst == FloatArg:
            reg = self.cgen.fetch_register('general')
            line1 = "mov %s, dword [%s] \n" % (reg, self.src)
            line2 = "mov dword [%s], %s \n" % (self.dest, reg)
            return line1 + line2
        else:
            raise ValueError("Unsuported types!", typ_dst, typ_src)


class StmAssignConst(Statement):
    def __init__(self, cgen, dest, const):
        self.cgen = cgen
        self.dest = dest
        self.const = const 

    def asm_code(self):
        typ = self.cgen.type_of(self.dest)
        if typ is None: #create local with type of const
            self.cgen.create_local(self.dest, self.const)
            typ = self.cgen.type_of(self.dest)
        if typ == IntArg:
            if not isinstance(self.const, int):
                raise ValueError('Type mismatch', typ, self.const)
            return 'mov dword [%s], %i \n' % (self.dest, self.const)
        elif typ == FloatArg:
            tmp = float(self.const) if isinstance(self.const, int) else self.const 
            if not isinstance(tmp, float):
                raise ValueError('Type mismatch', typ, self.const)
            fl = float2hex(tmp)
            return 'mov dword [%s], %s ;float value = %f \n' % (self.dest, fl, tmp)
        elif typ == Vector3Arg:
            raise NotImplementedError()
        else:
            raise ValueError('Unknown type of destination')

class StmAssignBinary(Statement):
    def __init__(self, cgen, dest, op1, op2, operator):
        self.cgen = cgen
        self.dest = dest
        self.op1 = op1
        self.op2 = op2
        self.operator = operator

    def asm_code(self):
        if is_num(self.op1) or is_num(self.op2): # a = 4 + b or a = b + 4.5
            if is_num(self.op1) and is_num(self.op2): # a = 4 + 9 or a = 2.3 + 9.8
                return self._asm_code_consts(self.op1, self.op2)
        else: # a = b + c
            typ_op1 = self.cgen.type_of(self.op1)
            typ_op2 = self.cgen.type_of(self.op2)
            if typ_op1 is None or typ_op2 is None:
                raise ValueError("Op1 or Op2 doesnt exist.", self.op1, self.op2)
            if typ_op1 == IntArg and typ_op2 == IntArg:
                return self._asm_code_ints()
            elif typ_op1 == FloatArg and typ_op2 == FloatArg:
                return self._asm_code_floats()
            elif typ_op1 == FloatArg and typ_op2 == IntArg: #conversions
                raise ValueError("TODO binary operation")
            elif typ_op1 == IntArg and typ_op2 == FloatArg:
                raise ValueError("TODO binary operation")
            else:
                raise ValueError("Type mismatch!", typ_op1, typ_op2)
        return None

    def _asm_code_consts(self, const1, const2):
        typ = self.cgen.type_of(self.dest)
        if isinstance(const1, float) or isinstance(const2, float):
            tmp = preform_arithmetic(float(const1), float(const2), self.operator)
        elif isinstance(const1, int) and isinstance(const2, int):
            tmp = preform_arithmetic(const1, const2, self.operator)
        else:
            raise ValueError("Unknown consts", const1, const2)

        if typ is None:
            self.cgen.create_local(self.dest, tmp)

        if typ == IntArg and not isinstance(tmp, int):
            raise ValueError("Type mismatch", typ, tmp)
        if typ == FloatArg and isinstance(tmp, int):
            tmp = float(tmp)
        
        if isinstance(tmp, int):
            return 'mov dword [%s], %i \n' % (self.dest, tmp)
        elif isinstance(tmp, float):
            fl = float2hex(tmp)
            return 'mov dword [%s], %s ;float value = %f \n' % (self.dest, fl, tmp)
        else:
            raise ValueError("Unsuported type of constant ", tmp)


    def _asm_code_ints(self):
        typ_dst = self.cgen.type_of(self.dest)
        if typ_dst is None:
            self.cgen.create_local(self.dest, 0)
        
        if self.operator == '/' or self.operator == '%':
            reg = self.cgen.fetch_register_exact('eax')
            reg2 = self.cgen.fetch_register_exact('edx')
            line1 = "mov %s, dword [%s] \n" % (reg, self.op1)
            line2 = "mov edx, 0 \n"
            line3 = "idiv dword [%s] \n" % self.op2
            if self.operator == '/':
                line4 = "mov dword [%s], %s \n" % (self.dest, reg)
            elif self.operator == '%':
                line4 = "mov dword [%s], %s \n" % (self.dest, reg2)
            return line1 + line2 + line3 + line4

        reg = self.cgen.fetch_register('general')
        line1 = "mov %s, dword [%s] \n" % (reg, self.op1)
        if self.operator == '+':
            line2 = "add %s, dword [%s] \n" % (reg, self.op2)
        elif self.operator == '-':
            line2 = "sub %s, dword [%s] \n" % (reg, self.op2)
        elif self.operator == '*':
            line2 = "imul %s, dword [%s] \n" % (reg, self.op2)
        else:
            raise ValueError("Unsuported operator.", self.operator)
        line3 = "mov dword [%s], %s \n" % (self.dest, reg)
        return line1 + line2 + line3

    def _asm_code_floats(self):
        typ_dst = self.cgen.type_of(self.dest)
        if typ_dst is None:
            self.cgen.create_local(self.dest, 0.0)
        reg = self.cgen.fetch_register('xmm')
        line1 = "movss %s, dword [%s] \n" % (reg, self.op1)
        if self.operator == '+':
            line2 = "addss %s, dword [%s] \n" % (reg, self.op2)
        elif self.operator == '-':
            line2 = "subss %s, dword [%s] \n" % (reg, self.op2)
        elif self.operator == '*':
            line2 = "mulss %s, dword [%s] \n" % (reg, self.op2)
        elif self.operator == '/':
            line2 = "divss %s, dword [%s] \n" % (reg, self.op2)
        else:
            raise ValueError("Unsuported operator.", self.operator)
        line3 = "movss dword [%s], %s \n" % (self.dest, reg)
        return line1 + line2 + line3

class StmAssignFunc(Statement):
    def __init__(self, cgen, dest, func, args):
        self.cgen = cgen
        self.dest = dest
        self.func = func
        self.args = args

    def asm_code(self):
        #asm code depentd type of name1 and name2
        # name can be integer, vector, float etc...
        # implicit conversions int to float etc...
        pass



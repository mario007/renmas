import struct
from .arg import  IntArg, FloatArg, Vector3Arg, StructArg

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

def _copy_to_regs(args):
    xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']
    code = ''
    for a in args:
        if isinstance(a, IntArg):
            code += "mov %s, dword [%s]\n" % (general.pop(), a.name)
        elif isinstance(a, FloatArg):
            code += "movss %s, dword [%s] \n" % (xmm.pop(), a.name)
        elif isinstance(a, Vector3Arg):
            code += "movaps %s, oword [%s] \n" % (xmm.pop(), a.name)
        else:
            raise ValueError('Unknown argument', a)
    return code

class Statement:
    def __init__(self):
        pass
    
    def asm_code(self):
        raise NotImplementedError()

def _load_int_to_reg(cgen, reg, src, src_path=None):
    if src_path is not None:
        reg2 = cgen.fetch_register('general')
        code = "mov %s, %s \n" % (reg2, src) #64-bit TODO
        arg = cgen.get_argument(src) # arg is StructArg TODO struct is input arg
        path = arg.typ.typ + "." + src_path
        code += "mov %s, dword [%s + %s]\n" % (reg, reg2, path)
    else:
        code = "mov %s, dword [%s] \n" % (reg, src)
    return code

def _store_int_from_reg(cgen, reg, dest, dst_path=None):
    if dst_path is not None:
        reg2 = cgen.fetch_register('general')
        arg = cgen.get_argument(dest) # arg is StructArg TODO struct is input arg
        path = arg.typ.typ + "." + dst_path
        code = "mov %s, %s \n" % (reg2, dest) #64-bit TODO
        code += "mov dword [%s + %s], %s\n" % (reg2, path, reg)
    else:
        code = "mov dword [%s], %s \n" % (dest, reg)
    return code

def _load_float_to_reg(cgen, reg, src, src_path=None): #reg must be xmm
    if src_path is not None:
        reg2 = cgen.fetch_register('general')
        code = "mov %s, %s \n" % (reg2, src) #64-bit TODO
        arg = cgen.get_argument(src) # arg is StructArg TODO struct is input arg
        path = arg.typ.typ + "." + src_path
        code += "movss %s, dword [%s + %s]\n" % (reg, reg2, path)
    else:
        code = "movss %s, dword [%s] \n" % (reg, src)
    return code

def _store_float_from_reg(cgen, reg, dest, dst_path=None):
    if dst_path is not None:
        reg2 = cgen.fetch_register('general')
        arg = cgen.get_argument(dest) # arg is StructArg TODO struct is input arg
        path = arg.typ.typ + "." + dst_path
        code = "mov %s, %s \n" % (reg2, dest) #64-bit TODO
        code += "movss dword [%s + %s], %s\n" % (reg2, path, reg)
    else:
        code = "movss dword [%s], %s \n" % (dest, reg)
    return code

def _load_vec3_to_reg(cgen, reg, src, src_path=None): #reg must be xmm
    if src_path is not None:
        reg2 = cgen.fetch_register('general')
        code = "mov %s, %s \n" % (reg2, src) #64-bit TODO
        arg = cgen.get_argument(src) # arg is StructArg TODO struct is input arg
        path = arg.typ.typ + "." + src_path
        code += "movaps %s, oword [%s + %s]\n" % (reg, reg2, path)
    else:
        code = "movaps %s, oword [%s] \n" % (reg, src)
    return code

def _store_vec3_from_reg(cgen, reg, dest, dst_path=None):
    if dst_path is not None:
        reg2 = cgen.fetch_register('general')
        arg = cgen.get_argument(dest) # arg is StructArg TODO struct is input arg
        path = arg.typ.typ + "." + dst_path
        code = "mov %s, %s \n" % (reg2, dest) #64-bit TODO
        code += "movaps oword [%s + %s], %s\n" % (reg2, path, reg)
    else:
        code = "movaps oword [%s], %s \n" % (dest, reg)
    return code


def _copy_int_to_int(cgen, dest, src, dst_path=None, src_path=None):
    reg = cgen.fetch_register('general')
    code = _load_int_to_reg(cgen, reg, src, src_path)
    code += _store_int_from_reg(cgen, reg, dest, dst_path)
    return code

def _copy_float_to_float(cgen, dest, src, dst_path=None, src_path=None):
    reg = cgen.fetch_register('xmm')
    code = _load_float_to_reg(cgen, reg, src, src_path)
    code += _store_float_from_reg(cgen, reg, dest, dst_path)
    return code

def _copy_vec3_to_vec3(cgen, dest, src, dst_path=None, src_path=None):
    reg = cgen.fetch_register('xmm')
    code = _load_vec3_to_reg(cgen, reg, src, src_path)
    code += _store_vec3_from_reg(cgen, reg, dest, dst_path)
    return code

def _convert_int_to_float(reg, to_reg):
    return "cvtsi2ss %s, %s \n" % (to_reg, reg)

def _copy_int_to_float(cgen, dest, src, dst_path=None, src_path=None):
    reg = cgen.fetch_register('general')
    to_reg = cgen.fetch_register('xmm')
    code = _load_int_to_reg(cgen, reg, src, src_path)
    code += _convert_int_to_float(reg, to_reg)
    code += _store_float_from_reg(cgen, to_reg, dest, dst_path)
    return code

#TODO --little optimization can be done if it is same structure
# --- it must use same general register for loading and storing 
class StmAssignName(Statement):
    def __init__(self, cgen, dest, src, dst_path=None, src_path=None):
        self.cgen = cgen
        self.dest = dest
        self.src = src
        self.dst_path = dst_path
        self.src_path = src_path

    def asm_code(self):
        #source argument must exist
        src_arg = self.cgen.get_argument(self.src, self.src_path)
        if src_arg is None:
            raise ValueError('Source argument %s doesnt exist' % self.src)
        if self.dst_path is not None: #soruce is struct argument
            dst_arg = self.cgen.get_argument(self.dest, self.dst_path)
            if dst_arg is None:
                raise ValueError('Destination struct %s doesnt exist' % self.dest)
        else:
            dst_arg = self.cgen.create_local(self.dest, self.src)

        if isinstance(src_arg, IntArg) and isinstance(dst_arg, IntArg):
            code = _copy_int_to_int(self.cgen, self.dest, self.src, self.dst_path, self.src_path)
        elif isinstance(src_arg, FloatArg) and isinstance(dst_arg, FloatArg):
            code = _copy_float_to_float(self.cgen, self.dest, self.src, self.dst_path, self.src_path)
        elif isinstance(src_arg, Vector3Arg) and isinstance(dst_arg, Vector3Arg):
            code = _copy_vec3_to_vec3(self.cgen, self.dest, self.src, self.dst_path, self.src_path)
        elif isinstance(src_arg, IntArg) and isinstance(dst_arg, FloatArg):
            code = _copy_int_to_float(self.cgen, self.dest, self.src, self.dst_path, self.src_path)
        else:
            raise ValueError('Type mismatch', src_arg, dst_arg)
        return code

def _copy_const_int_to(cgen, dest, const, path=None):
    if path is not None:
        arg = cgen.get_argument(dest) # arg is StructArg TODO struct is input arg
        reg = cgen.fetch_register('general')
        line1 = "mov %s, %s \n" % (reg, dest) #64-bit TODO
        path = arg.typ.typ + "." + path
        line2 = "mov dword [%s + %s], %i\n" % (reg, path, const)
        return line1 + line2
    else:
        return 'mov dword [%s], %i \n' % (dest, const)

def _copy_const_float_to(cgen, dest, const, path=None, offset=None):
    if path is not None:
        arg = cgen.get_argument(dest) # arg is StructArg TODO struct is input arg
        reg = cgen.fetch_register('general')
        line1 = "mov %s, %s \n" % (reg, dest) #64-bit TODO
        path = arg.typ.typ + "." + path
        line2 = "mov dword [%s + %s], %i\n" % (reg, path, const)
        return line1 + line2
    else:
        fl = float2hex(float(const))
        if offset is None:
            return 'mov dword [%s], %s ;float value = %f \n' % (dest, fl, float(const))
        else:
            return 'mov dword [%s + %i], %s ;float value = %f \n' % (dest, offset, fl, float(const))

class StmAssignConst(Statement):
    def __init__(self, cgen, dest, const, path=None):
        self.cgen = cgen
        self.dest = dest
        self.const = const 
        self.path = path

    def asm_code(self):
        arg = self.cgen.create_local(self.dest, self.const, self.path)
        typ = type(arg)
        if typ == IntArg:
            if not isinstance(self.const, int):
                raise ValueError('Type mismatch', typ, self.const)
            code = _copy_const_int_to(self.cgen, self.dest, self.const, self.path)
        elif typ == FloatArg:
            tmp = float(self.const) if isinstance(self.const, int) else self.const 
            if not isinstance(tmp, float):
                raise ValueError('Type mismatch', typ, self.const)
            code = _copy_const_float_to(self.cgen, self.dest, self.const, self.path)
        elif typ == Vector3Arg:
            if (isinstance(self.const, tuple) or isinstance(self.const, list)) and len(self.const) == 3:
                code = _copy_const_float_to(self.cgen, self.dest, float(self.const[0]), self.path)
                code += _copy_const_float_to(self.cgen, self.dest, float(self.const[1]), self.path, offset=4)
                code += _copy_const_float_to(self.cgen, self.dest, float(self.const[2]), self.path, offset=8)
                code += _copy_const_float_to(self.cgen, self.dest, 0.0, self.path, offset=12)
            else:
                raise ValueError('Type mismatch',  arg, self.const)
        else:
            raise ValueError('Unknown type of destination')
        return code

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

class StmCall(Statement):
    def __init__(self, cgen, func, args):
        self.cgen = cgen
        self.func = func
        self.args = args

    def asm_code(self):
        if not self.cgen.func_exist(self.func):
            raise ValueError("Function %s doesnt exist!" % self.func)

        input_args = self.cgen.input_args(self.func)
        
        arguments = []
        for a in self.args:
            arg = self.cgen.fetch_argument(a)
            if arg is None:
                raise ValueError("Argument %s doenst exist!", a)
            arguments.append(arg)

        if len(input_args) != len(arguments):
            raise ValueError("Argument lengtsh doesnt match", input_args, arguments)
        
        for arg1, arg2 in zip(input_args, arguments):
            if type(arg1) != type(arg2):
                raise ValueError("Argument type mismatch", arg1, arg2)

        code = _copy_to_regs(arguments)
        code += "call %s\n" % self.func
        return code



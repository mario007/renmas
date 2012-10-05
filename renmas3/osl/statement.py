import struct
import platform
from .arg import  IntArg, FloatArg, Vector3Arg, StructArg, Attribute
from .cgen import register_function

from .instr import load_struct_ptr
from .instr import load_int_into_reg, load_float_into_reg, load_vec3_into_reg
from .instr import store_int_from_reg, store_float_from_reg, store_vec3_from_reg
from .instr import copy_int_to_int, copy_float_to_float, copy_vec3_to_vec3, copy_int_to_float
from .instr import store_const_into_mem, convert_float_to_int, convert_int_to_float

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

def _copy_to_regs(cgen, args, input_args):
    if len(args) != len(input_args):
        raise ValueError("Argument length mismatch", args, input_args)

    xmm = ['xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
    general = ['esi', 'edx', 'ecx', 'ebx', 'eax']
    ptr_reg = 'ebp'
    ptr_reg2 = 'edi'
    tmp_xmm = 'xmm7'
    bits = platform.architecture()[0]

    code = ''
    for arg1, arg2 in zip(args, input_args):
        if isinstance(arg1, int):
            if type(arg2) == IntArg:
                reg = general.pop()
                code += "mov %s, %i\n" % (reg, arg1)
            elif type(arg2) == FloatArg:
                raise ValueError("Konverzija float konstante-temp variabla?")
            else:
                raise ValueError("Type mismatch", arg1, arg2)
        elif isinstance(arg1, float):
            raise ValueError("Float argument-temp const variable?", arg1)
        elif isinstance(arg1, str) or isinstance(arg1, Attribute):
            a = cgen.get_arg(arg1)
            if a is None:
                raise ValueError("Argument %s doesn't exist!" % name)
            if type(a) == IntArg:
                if type(arg2) == IntArg:
                    reg = general.pop()
                    code += load_int_into_reg(cgen, reg, arg1, ptr_reg)
                elif type(arg2) == FloatArg:
                    to_reg = xmm.pop()
                    code += load_int_into_reg(cgen, ptr_reg2, arg1, ptr_reg)
                    code += convert_int_to_float(ptr_reg2, to_reg)
                else:
                    raise ValueError("Type mismatch", a, arg2)
            elif type(a) == FloatArg and type(arg2) == FloatArg:
                reg = xmm.pop()
                code += load_float_into_reg(cgen, reg, arg1, ptr_reg)
            elif type(a) == Vector3Arg and type(arg2) == Vector3Arg:
                reg = xmm.pop()
                code += load_vec3_into_reg(cgen, reg, arg1, ptr_reg)
            elif type(a) == StructArg and type(arg2) == StructArg:
                reg = general.pop()
                if bits == '64bit':
                    reg = 'r' + reg[1:]
                    c, dummy, dummy = load_struct_ptr(cgen, arg1, reg)
                else:
                    c, dummy, dummy = load_struct_ptr(cgen, arg1, reg)
                code += c
            else:
                raise ValueError("Unsuported argument type, mismatch", a, arg2)
        else:
            raise ValueError("Unsupprted argument for shader!", arg1, arg2)
    return code


class Statement:
    def __init__(self):
        pass
    
    def asm_code(self):
        raise NotImplementedError()

class StmAssignName(Statement):
    #def __init__(self, cgen, dest, src, dst_path=None, src_path=None):
    def __init__(self, cgen, dest, src):
        self.cgen = cgen
        self.dest = dest
        self.src = src

    def asm_code(self):
        #source argument must exist
        src_arg = self.cgen.get_arg(self.src)
        if src_arg is None:
            raise ValueError('Source argument %s doesnt exist' % self.src)
        dst_arg = self.cgen.create_arg(self.dest, self.src)

        if isinstance(src_arg, IntArg) and isinstance(dst_arg, IntArg):
            code = copy_int_to_int(self.cgen, self.dest, self.src)
        elif isinstance(src_arg, FloatArg) and isinstance(dst_arg, FloatArg):
            code = copy_float_to_float(self.cgen, self.dest, self.src)
        elif isinstance(src_arg, Vector3Arg) and isinstance(dst_arg, Vector3Arg):
            code = copy_vec3_to_vec3(self.cgen, self.dest, self.src)
        elif isinstance(src_arg, IntArg) and isinstance(dst_arg, FloatArg):
            code = copy_int_to_float(self.cgen, self.dest, self.src)
        else:
            raise ValueError('Type mismatch', src_arg, dst_arg)
        return code

class StmAssignConst(Statement):
    def __init__(self, cgen, dest, const):
        self.cgen = cgen
        self.dest = dest
        self.const = const 

    def asm_code(self):
        arg = self.cgen.create_arg(self.dest, self.const)
        typ = type(arg)
        if typ == IntArg:
            if not isinstance(self.const, int):
                raise ValueError('Type mismatch', typ, self.const)
            code = store_const_into_mem(self.cgen, self.dest, self.const)
        elif typ == FloatArg:
            tmp = float(self.const) if isinstance(self.const, int) else self.const 
            if not isinstance(tmp, float):
                raise ValueError('Type mismatch', typ, self.const)
            code = store_const_into_mem(self.cgen, self.dest, self.const)
        elif typ == Vector3Arg:
            if (isinstance(self.const, tuple) or isinstance(self.const, list)) and len(self.const) == 3:
                code = store_const_into_mem(self.cgen, self.dest, float(self.const[0]))
                code += store_const_into_mem(self.cgen, self.dest, float(self.const[1]), offset=4)
                code += store_const_into_mem(self.cgen, self.dest, float(self.const[2]), offset=8)
                code += store_const_into_mem(self.cgen, self.dest, 0.0, offset=12)
            else:
                raise ValueError('Type mismatch',  arg, self.const)
        else:
            raise ValueError('Unknown type of destination', arg, self.const)
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
                raise ValueError("Argument %s doesnt exist!", a)
            arguments.append(arg)

        if len(input_args) != len(arguments):
            raise ValueError("Argument lengtsh doesnt match", input_args, arguments)
        
        for arg1, arg2 in zip(input_args, arguments):
            if type(arg1) != type(arg2):
                raise ValueError("Argument type mismatch", arg1, arg2)

        code = _copy_to_regs_old(arguments)
        code += "call %s\n" % self.func
        return code

class StmAssignCall(Statement):
    def __init__(self, cgen, dest, func, args):
        self.cgen = cgen
        self.dest = dest
        self.func = func
        self.args = args

    def asm_code(self):

        f = self.cgen.get_function(self.func)
        if f is not None:
            func, ret_type = f
            code = func(self.cgen, self.args)
            arg = self.cgen.create_arg(self.dest, typ=ret_type)
            if type(arg) != ret_type:
                raise ValueError("Type mismatch!", arg, ret_type)

        s = self.cgen.get_shader(self.func)
        if s is not None:
            code = _copy_to_regs(self.cgen, self.args, s.input_args)
            code += "call %s\n" % self.func
            ret_type = s.ret_type

        if f is None and s is None:
            raise ValueError("Both function and shader doesnt exist")

        dst = self.cgen.get_arg(self.dest)
        if dst is None:
            dst = self.cgen.create_arg(self.dest, typ=ret_type)

        self.cgen.clear_regs()
        if ret_type == IntArg and type(dst) == IntArg:
            reg = self.cgen.register(reg="eax")
            store = store_int_from_reg(self.cgen, reg, self.dest)
        elif ret_type == FloatArg and type(dst) == FloatArg:
            reg = self.cgen.register(reg="xmm0")
            store = store_float_from_reg(self.cgen, reg, self.dest)
        elif type(dst) == FloatArg and ret_type == IntArg:
            reg = self.cgen.register(reg="eax")
            to_reg = self.cgen.register(reg="xmm0")
            store = convert_int_to_float(reg, to_reg)
            store += store_float_from_reg(self.cgen, to_reg, self.dest)
        elif ret_type == Vector3Arg and type(dst) == Vector3Arg:
            reg = self.cgen.register(reg="xmm0")
            store = store_vec3_from_reg(self.cgen, reg, self.dest)
        elif ret_type == StructArg:
            raise ValueError("Unsupported argument returned type!", ret_type, dst)
        else:
            raise ValueError("Type mismatch", ret_type, dst)
        return code + store

class StmReturn(Statement):
    def __init__(self, cgen, const=None, src=None):
        self.cgen = cgen
        self.const = const
        self.src = src

    def asm_code(self):
        if self.const is None and self.src is None:
            return "ret \n"
        if self.const is not None:
            if isinstance(self.const, int):
                self.cgen.register_ret_type(IntArg)
                code = "mov eax, %i \n" % self.const
                code += "ret \n"
                return code
            elif isinstance(self.const, float):
                self.cgen.register_ret_type(FloatArg)
                raise ValueError("Argument const float ", self.const)
            elif isinstance(self.const, tuple) or isinstance(self.const, list):
                raise ValueError("Return is const list or tuple ", self.const)
            else:
                raise ValueError("Unsuported constant", self.const)
        arg = self.cgen.get_arg(self.src)
        if arg is None:
            raise ValueError("Argument doesnt exist.", self.src)
        self.cgen.register_ret_type(type(arg))
        self.cgen.clear_regs()
        if isinstance(arg, IntArg):
            reg = self.cgen.register(reg="eax")
            code = load_int_into_reg(self.cgen, reg, self.src)
        elif isinstance(arg, FloatArg):
            reg = self.cgen.register(reg="xmm0")
            code = load_float_into_reg(self.cgen, reg, self.src)
        elif isinstance(arg, Vector3Arg):
            reg = self.cgen.register(reg="xmm0")
            code = load_vec3_into_reg(self.cgen, reg, self.src)
        else:
            raise ValueError("Unsuported return argument!", arg)
        code += "ret \n"
        return code

def _int_function(cgen, args):
    if len(args) == 0:
        return "mov eax, 0\n"
    if len(args) != 1:
        raise ValueError("Wrong number of arguments", args)
    arg = args[0]
    if isinstance(arg, int):
        return "mov eax, %i\n" % arg
    elif isinstance(arg, float):
        return "mov eax, %i\n" % int(arg)
    elif isinstance(arg, str) or isinstance(arg, Attribute):
        cgen.clear_regs()
        a = cgen.get_arg(arg)
        if a is None:
            raise ValueError("Argument %s doesn't exist!" % name)
        if isinstance(a, IntArg):
            reg = cgen.register(reg="eax")
            code = load_int_into_reg(cgen, reg, arg)
            return code
        elif isinstance(a, FloatArg):
            reg = cgen.register(reg="xmm0")
            to_reg = cgen.register(reg="eax")
            code = load_float_into_reg(cgen, reg, arg)
            code += convert_float_to_int(reg, to_reg)
            return code
        else:
            raise ValueError("Unsupprted argument for int function!", a)
    else:
        raise ValueError('Unsupported argument')

register_function('int', _int_function, IntArg) 



def conv_int_to_float(cgen, reg, xmm):
    #TODO --- test that reg is general and xmm is xmm
    if cgen.AVX:
        return "vcvtsi2ss %s, %s, %s \n" % (xmm, xmm, reg)
    else:
        return "cvtsi2ss %s, %s \n" % (xmm, reg)

def conv_float_to_int(cgen, reg, xmm):
    #TODO --- test that reg is general and xmm is xmm
    if cgen.AVX:
        return "vcvttss2si %s, %s \n" % (reg, xmm)
    else:
        return "cvttss2si %s, %s \n" % (reg, xmm)

def check_ptr_reg(cgen, ptr_reg):
    if ptr_reg is None:
        raise ValueError("If vector is attribute register pointer is also required")

    if cgen.BIT64 and cgen.regs.is_reg32(ptr_reg):
        raise ValueError("Pointer register must be 64-bit!", ptr_reg)
    if not cgen.BIT64 and cgen.regs.is_reg64(ptr_reg):
        raise ValueError("Pointer register must be 32-bit!", ptr_reg)

class Argument:
    """
    Abstract base class that define interface for type in shading language.
    All supported types in shading language must inherit this class.
    """
    def __init__(self, name):
        """Name of the argument."""
        self.name = name

    @classmethod
    def set_value(cls, ds, value, path, idx_thread=None):
        """Store number in data section."""
        raise NotImplementedError()

    @classmethod
    def get_value(cls, ds, path, idx_thread=None):
        """Load number form data section."""
        raise NotImplementedError()

    def generate_data(self):
        """Generate code for local variable in #DATA section."""
        raise NotImplementedError()

    def load_cmd(self, cgen, dest_reg=None):
        """Generate code that load number from memory location to register."""
        raise NotImplementedError()

    def store_cmd(self, cgen, reg):
        """Generate code that store number from register to memory location."""
        raise NotImplementedError()

    @classmethod
    def neg_cmd(cls, cgen, reg):
        """Generate arightmetic code that negates number."""
        raise NotImplementedError()

    @classmethod
    def arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        """Generate code for arithmetic operation between registers."""
        raise NotImplementedError()

    @classmethod
    def rev_arith_cmd(cls, cgen, reg1, reg2, typ2, operator):
        """Generate code for arithmetic operation between registers."""
        raise NotImplementedError()

    @classmethod
    def supported(cls, operator, typ):
        """Return true if arithmetic with specified type is suppored."""
        raise NotImplementedError()

    @classmethod
    def item_supported(cls, typ):
        """Only for array types. Is array accepts this type of items."""
        return False

    @classmethod
    def register_type(cls):
        """Return type of register where argument is loaded."""
        raise NotImplementedError()


#TODO implement locking of map and list???-think
class ArgumentList:
    def __init__(self, args=[]):
        self._args = []
        for a in args:
            self._args.append(a)

    def __contains__(self, arg):
        return arg in self._args

    def __iter__(self):
        for a in self._args:
            yield a

    def __len__(self):
        return len(self._args)

class ArgumentMap:
    def __init__(self, args=[]):
        self._args = {}
        for a in args:
            self.add(a)

    def add(self, arg):
        if not isinstance(arg, Argument):
            raise ValueError("Wrong argument type", arg)

        if arg.name in self._args:
            raise ValueError("Argument %s allready exist", arg.name)
        self._args[arg.name] = arg

    def __contains__(self, name):
        return name in self._args

    def __getitem__(self, name):
        return self._args[name]

    def __iter__(self):
        for a in self._args.items():
            yield a

class Attribute:
    def __init__(self, name, path):
        self.name = name #name of struct
        self.path = path #path to member in struct

class Callable:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Operations:
    def __init__(self, operations):
        self.operations = operations

class Const:
    def __init__(self, const):
        self.const = const

class Name:
    def __init__(self, name):
        self.name = name

class Subscript:
    def __init__(self, name, index, path=None):
        self.name = name
        self.index = index
        #if we have path than this is array in struct
        self.path = path #path to member in struct

class EmptyOperand:
    pass

class Operation:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right



from .arg import create_argument

class CodeGenerator:
    def __init__(self, args={}):
        self._args = args
        self._statements = []

    def add_stm(self, stm):
        self._statements.append(stm)

    def _generate_data_section(self):
        data = ''
        for arg in self._args.values():
            data += arg.generate_data()
        for arg in self._locals.values():
            data += arg.generate_data()
        return data

    def generate_code(self):
        self._locals = {}
        code = ''
        for s in self._statements:
            self.clear_regs()
            code += s.asm_code()
        data = self._generate_data_section() + '\n'
        data = "\n#DATA \n" + data + "#CODE \n"
        return data + code + '#END \n'

    #create const it it's doesnt exist
    def fetch_const(self, value):
        pass

    def fetch_argument(self, name):
        #consts?
        if name in self._args:
            return self._args[name]
        if name in self._locals:
            return self._locals[name]
        return None

    def create_local(self, name , value):
        #consts?? - const with that name exist
        if name in self._args or name in self._locals:
            # assert?
            raise ValueError('Local %s allready exist!' % name)
        if isinstance(value, str):
            arg =  self.fetch_argument(value)
            value = arg.value
        self._locals[name] = create_argument(name, value) 

    def fetch_register(self, reg_type):
        if reg_type == 'xmm':
            return self._xmm.pop()
        elif reg_type == 'general':
            return self._general.pop()
        else:
            raise ValueError('Unknown type of register', reg_type)

    def fetch_register_exact(self, reg):
        if reg in self._xmm:
            self._xmm.remove(reg)
            return reg
        if reg in self._general:
            self._general.remove(reg)
            return reg
        return None

    # clear ocupied registers
    def clear_regs(self):
        self._xmm = ['xmm7', 'xmm6', 'xmm5', 'xmm4', 'xmm3', 'xmm2', 'xmm1', 'xmm0']
        self._general = ['ebp', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'eax']

    def type_of(self, name):
        if name in self._args:
            return type(self._args[name])
        if name in self._locals:
            return type(self._locals[name])
        return None



import platform
from renmas2.core import Vector3

class Param:
    def __init__(self, name, typ, val, output):
        self.name = name
        self.typ = typ
        self.val = val
        self.output = output

    def to_asm(self):
        #TODO -- init val
        if self.typ == "int":
            return "int32 " + self.name
        elif self.typ == "float":
            return "float " + self.name
        elif self.typ == "vector":
            return "float " + self.name + "[4]"
        else: #we assume it is complex param - structure
            # we need pointer to structure
            bits = platform.architecture()[0]
            if bits == "64bit":
                return "uint64 %s" % self.name
            else:
                return "uint32 %s" % self.name

    def copy_from_reg(self, reg):
        if self.typ == "int": # mov dword [name], eax
            reg = 'e' + reg[1:]
            return "mov dword[%s], %s " % (self.name, reg)
        elif self.typ == "float":
            reg = 'e' + reg[1:]
            return "mov dword[%s], %s " % (self.name, reg)
        elif self.typ == "vector": # macro eq128 name = eax {xmm7}
            return "macro eq128 %s = %s {xmm7}" % (self.name, reg)
        else: #we assume it is complex param - structure
            # we need pointer to structure
            bits = platform.architecture()[0]
            if bits == "64bit":
                return "mov qword[%s], %s " % (self.name, reg)
            else:
                return "mov dword[%s], %s " % (self.name, reg)

class Constant:
    def __init__(self, name, typ, val):
        self.name = name
        self.typ = typ
        self.val = val

class Statement:
    def __init__(self, asm_code):
        self.code = asm_code

class LocalVar:
    def __init__(self, name, typ, val):
        self.name = name
        self.typ = typ
        self.val = val

    def to_asm(self):
        #TODO -- init val
        if self.typ == "int":
            return "int32 " + self.name
        elif self.typ == "float":
            return "float " + self.name
        elif self.typ == "vector":
            return "float " + self.name + "[4]"
        else: #we assume it is complex param - structure
            return "%s %s" % (self.typ, self.name) 

class Constant:
    def __init__(self, name, typ, val):
        self.name = name
        self.typ = typ
        self.val = val

    def to_asm(self):
        if self.typ == "int":
            return "int32 " + self.name + " = " + str(int(self.val))
        elif self.typ == "float":
            return "float " + self.name + " = " + str(float(self.val))
        elif self.typ == "vector":
            return ValueError("Not suported vector constant type") 
            return "float " + self.name + "[4]" + " = " + str(self.val)
        else:
            return ValueError("Not suported constant type") 

def _set_float(lst_ds, name, value):
    for ds in lst_ds:
        ds[name] = float(value)

def _get_float(lst_ds, name):
    return lst_ds[0][name]

def _set_vector(lst_ds, name, value):
    if isinstance(value, Vector3):
        val = (value.x, value.y, value.z, 0.0)
    else:
        val = (float(value[0]), float(value[1]), float(value[2]), 0.0)
    for ds in lst_ds:
        ds[name] = val 

def _get_vector(lst_ds, name):
    return lst_ds[0][name][0:3]

_setters = {'float': _set_float, 'vector': _set_vector}
_getters = {'float': _get_float, 'vector': _get_vector}

class Props:
    def __init__(self, props, ds):
        self.__dict__['_props'] = props 
        self.__dict__['_ds'] = ds 

    def __getattr__(self, name):
        if name in self._props:
            return _getters[self._props[name].typ](self._ds, name)
        try:
            return self.__dict__[name]
        except:
            raise AttributeError("Attribute " + name + " doesn't exist!")

    def __setattr__(self, name, value):
        if name in self._props:
            _setters[self._props[name].typ](self._ds, name, value)
        else:
            raise AttributeError("Attribute " + name + " doesn't exist!")

class Shader:
    def __init__(self, name, typ, params, statements, localvars, constants):
        self.name = name
        self.typ = typ
        self.params = params
        self.statements = statements
        self.localvars = localvars
        self.constants = constants
        self._ds = []

    def __repr__(self):

        txt =  "Shader type = " +  self.typ + " Shader name =" + self.name + "\n"
        txt += "Shader parameters \n"
        for p in self.params:
            txt += 'Param name = ' + p.name + ',  ptype = ' + p.typ + ',  val =' + str(p.val) + ",  output = " + str(p.output) + "\n"

        txt += "\nLocals \n"
        for l in self.localvars.values():
            txt += l.to_asm() + "\n"
        txt += "\nStatements \n"
        for s in self.statements:
            txt += s.code + "\n"

        txt += self.generate_code("test_label") + "\n"
        return txt

    def prepare(self, label, runtimes, assembler):
        asm_code = self.generate_code(label)
        
        self._ds = []
        self._runtimes = runtimes
        self._label = label
        #TODO think -- caching mc
        mc = assembler.assemble(asm_code)
        for r in runtimes:
            ds = r.load(label, mc)
            self._ds.append(ds)
        
        self.props = Props(self.localvars, self._ds)
        # 5. use DataSection for populating parameters and local parameters
        # 6. use label for name in Runtime and for global labels

    def execute(self):
        self._runtimes[0].run(self._label)

    def generate_code(self, label):
        data = "#DATA \n"
        for p in self.params:
            data +=  p.to_asm() + "\n"
        for l in self.localvars.values():
            data += l.to_asm() + "\n"
        for c in self.constants.values():
            data += c.to_asm() + "\n"
        #TODO think -- label
        # eax - p1 , ebx - p2, ecx - p3, edx - p4, esi - p5 , edi - p6
        # complex params are passed through pointers(references)
        bits = platform.architecture()[0]
        if bits == "64bit":
            regs = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi']
        else:
            regs = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']
        code = "#CODE \n"
        code += "global %s: \n" % label  
        for p, reg in zip(self.params, regs):
            code += p.copy_from_reg(reg) + "\n"
        for s in self.statements:
            code += s.code + "\n"
        code += "#END \n"

        asm_code = data + code 
        return asm_code

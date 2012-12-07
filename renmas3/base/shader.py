import x86
from tdasm import Tdasm
from .arg import Struct

class Shader:
    def __init__(self, name, code, args, input_args=None, shaders=None,
            ret_type=None, func=False, functions=None):
        self._name = name
        self._code = code
        self._args = args
        self._input_args = input_args
        if self._input_args is None:
            self._input_args = []
        
        self._shaders = shaders
        if self._shaders is None:
            self._shaders = []

        self._functions = functions
        if self._functions is None:
            self._functions = []

        self._ret_type = ret_type
        self._ds = []
        self._struct_args = {}
        self._func = func 
        self._mc_cache = {}
        for key, arg in iter(args):
            if isinstance(arg, Struct):
                self._struct_args.update(arg.paths)

    @property
    def ret_type(self):
        return self._ret_type

    @property
    def name(self):
        return self._name

    @property
    def input_args(self):
        return self._input_args

    def prepare(self, runtimes):
        for s in self._shaders:
            s.prepare(runtimes)

        self._runtimes = runtimes
        asm = Tdasm()
        name = 'shader' + str(id(self))

        for r in runtimes:
            for f in self._functions:
                label, code = f
                if not r.global_exists(label):
                    if label in self._mc_cache:
                        r.load(label, self._mc_cache[label])
                    else:
                        mc = asm.assemble(code, True)
                        self._mc_cache[label] = mc
                        r.load(label, mc)

        ds = []
        for r in runtimes:
            if not r.global_exists(self._name):
                if self._name in self._mc_cache:
                    ds.append(r.load(name, self._mc_cache[self._name])) 
                else:
                    mc = asm.assemble(self._code, self._func)
                    self._mc_cache[self._name] = mc
                    ds.append(r.load(name, mc)) 
        if ds:
            self._ds = ds


    def execute(self):
        if len(self._runtimes) == 1:
            name = 'shader' + str(id(self))
            self._runtimes[0].run(name)
        else:
            name = 'shader' + str(id(self))
            addrs = [r.address_module(name) for r in self._runtimes]
            x86.ExecuteModules(tuple(addrs))

    def get_value(self, name, idx_thread=None):
        if name in self._args:
            return self._args[name].get_value(self._ds, name, idx_thread)
        elif name in self._struct_args:
            return self._struct_args[name].get_value(self._ds, name, idx_thread)
        else:
            raise ValueError("Wrong name of argument", name)

    def set_value(self, name, value, idx_thread=None):
        if name in self._args:
            return self._args[name].set_value(self._ds, value, name, idx_thread)
        elif name in self._struct_args:
            return self._struct_args[name].set_value(self._ds, value, name, idx_thread)
        else:
            raise ValueError("Wrong name of argument", name)

class Properties:
    def __init__(self):
        self._props = {}

    def get_value(self, name):
        return self._props[name].value

    def set_value(self, name, value):
        self._props[name].value = value

    def add(self, props):
        for p in props:
            if p.name in self._props:
                raise ValueError("Property %s allready exist" % p.name)
            self._props[p.name] = p

class GeneralShader:
    def __init__(self, name=None, code=None, py_code=None, props=None):
        self._default_code = code
        self._default_py_code = py_code
        if props is None:
            props = []
        self._default_props = props

        self._code = code
        self._py_code = py_code
        self._name = name
        if name is None:
            self._name = 'name' + str(id(self)) 

        self._props = Properties()
        if props is not None:
            self._props.add(props)

    @property
    def props(self):
        return self._props

    def set_code(self, code=None, py_code=None):
        self._code = code
        self._py_code = py_code

    ## reset to state he was when it is created
    # this will be usefull so that we can easly
    # from gui return shader to initial state
    def reset(self):
        self._code = self._default_code
        self._py_code = self._default_py_code

        self._props = Properties()
        self._props.add(self._default_props)

    def prepare(self, runtimes, shaders=None):
        # 1. Prepare shader for execution
        # 2. runtimes(multicore problem) clone ??
        # 3. Throw exception if we don't have shader code
        pass

    #stand alone shader
    def execute(self):
        pass

    #stand_alone_shader
    def execute_py(self, *args):
        return self._py_code(self._props, *args)

    #return shader object so that other shader can call this shader
    def shader(self):
        pass


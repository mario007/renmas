import x86
from tdasm import Tdasm
from .arg import Struct, create_argument, arg_from_value, ArgumentMap, ArgumentList

class Shader:
    def __init__(self, name, asm_code, args, input_args=None, shaders=None,
            ret_type=None, func=False, functions=None):
        self._name = name
        self._code = asm_code
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
        self._runtimes = None
        #NOTE this is callable that must load some additionaly code
        # that is dynamically created like code for intersection
        # that depends on how many different shapes we have
        self.loader = None

    @property
    def nthreads(self):
        if self._runtimes is None:
            raise ValueError("Shader is not yet created!")
        return len(self._runtimes)

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
        if self.loader:
            self.loader(runtimes)

        for s in self._shaders:
            s.prepare(runtimes)

        self._runtimes = runtimes
        asm = Tdasm()
        name = 'shader' + str(id(self))

        for r in runtimes:
            for label, code in self._functions.items():
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


    def execute(self, nthreads=1):
        #FIXME fix this correctly
        if len(self._runtimes) == 1:
            name = 'shader' + str(id(self))
            self._runtimes[0].run(name)
        else: #we can prepare more that we can actually run
            name = 'shader' + str(id(self))
            addrs = [r.address_module(name) for r in self._runtimes]
            #addrs = [self._runtimes[idx].address_module(name) for idx in range(nthreads)]
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

    def __getstate__(self):
        d = {}
        d['name'] = self._name
        d['code'] = self._code
        d['args'] = self._args
        d['input_args'] = self._input_args
        d['shaders'] = self._shaders
        d['functions'] = self._functions
        d['ret_type'] = self._ret_type
        d['func'] = self._func
        return d

    def __setstate__(self, state):
        self._name = state['name']
        self._code = state['code']
        self._args = state['args']
        self._input_args = state['input_args']
        self._shaders = state['shaders']
        self._functions = state['functions']
        self._ret_type = state['ret_type']
        self._func = state['func']
        self.loader = None

        self._ds = []
        self._struct_args = {}
        self._mc_cache = {}
        for key, arg in iter(self._args):
            if isinstance(arg, Struct):
                self._struct_args.update(arg.paths)
        self._runtimes = None

def create_shader(name, source, args, input_args=[], shaders=[], func=False):
    from .parser import Parser
    from .cgen import CodeGenerator

    parser = Parser()
    cgen = CodeGenerator(name, args, input_args, shaders, func)
    parser.parse(source, cgen)
    shader = cgen.create_shader()
    return shader

class BaseShader:
    """Abstract base class for python shaders. It implements basic functionallity 
    for shaders. Derivied class must implement get_props, arg_map and arg_list
    methods."""

    def __init__(self, code, py_code):
        self._code = code
        self._py_code = py_code
        self._py_func = None
        if py_code is not None:
            self._py_func = self._create_func(py_code)
        self._shader = None

    def _create_func(self, code):
        d = {}
        exec(code, globals(), d)
        if len(d) != 1:
            raise ValueError("Only one key is expected in dict, function key!")
        key, func = d.popitem()
        return func

    @property
    def shader(self):
        """Return underlaying shader. It can return None if shader is not\
                yet created."""
        return self._shader

    def prepare(self, runtimes, shaders=[]):
        """Create underlaying shader and prepare it for execution."""

        if len(runtimes) > 32:
            raise ValueError("Maximum number of allowed treads is 32!")

        args = self.arg_map()
        in_args = self.arg_list()
        name = self.method_name()
        func = not self.standalone()

        self._shader = create_shader(name, self._code, args,
                                     input_args=in_args, shaders=shaders, func=func)

        self._shader.prepare(runtimes)
        self.update()

    def update(self):
        """Update public properties of shader."""

        if self._shader is None:
            raise ValueError("Cannot update shader properties because shader\
                    is not yet created!")

        props = self.get_props(self._shader.nthreads)
        if isinstance(props, dict):
            for key, value in props.items():
                for idx in range(self._shader.nthreads):
                    self._shader.set_value(key, value, idx_thread=idx)
        else: #update every thread with own properties
            if len(props) != self._shader.nthreads:
                raise ValueError("Wrong number of public properties(multithreading)!")
            for idx, prop in enumerate(props):
                for key, value in prop.items():
                    self._shader.set_value(key, value, idx_thread=idx)

    def execute(self):
        """Run execution of compiled shader."""
        if not self.standalone():
            raise ValueError('Only standalone shader can be executed directly.')
        if self._shader is None:
            raise ValueError('Shader is not yet prepared for execution.')
        self._shader.execute()

    def execute_py(self, *args):
        """Run execution of python shader."""
        if self._py_func is None:
            raise ValueError("Code for python shader is missing!")
        #NOTE python shaders doesn't support multithreading for now
        return self._py_func(self.get_props(1), *args)

    def standalone(self):
        """Return wethever this shader can be executed directly."""
        return True

    def method_name(self):
        """Return name that other shaders will use to call this shader."""
        return 'generic_shader_' + str(id(self))

    def get_props(self, nthreads):
        """Return dict of public properties. If properties for different threads
        have different values return array of dict. One dict for every thread."""
        raise NotImplementedError()

    def arg_map(self):
        """Create argument map for global arguments of shader."""
        raise NotImplementedError()

    def arg_list(self):
        """Create argument list for calling arguments of shader."""
        raise NotImplementedError()

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_py_func']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if self._py_code is not None:
            self._py_func = self._create_func(self._py_code)

class BasicShader(BaseShader):
    """Implementation of simple generic shader that is used to preform intesive
    coputation."""

    def __init__(self, code, py_code, props,
                 input_args=None, standalone=True, method_name=None):
        super(BasicShader, self).__init__(code, py_code)

        self.props = props
        self._standalone = standalone
        self._method_name = method_name
        self.input_args = input_args

    def arg_map(self):
        p = self.props
        if not isinstance(self.props, dict):
            p = self.props[0]
        args = ArgumentMap(arg_from_value(key, value) for key, value in p.items())
        return args

    def arg_list(self):
        if self.input_args is None:
            return ArgumentList()
        args = ArgumentList(arg_from_value(name, value, True)
                                    for name, value in self.input_args)
        return args

    def method_name(self):
        if self._method_name is None:
            return 'generic_shader_' + str(id(self))
        return self._method_name

    def get_props(self, nthreads):
        #NOTE: if properties for one thread is requested and we have multiple
        #      sets of properties we only return first set of properties 
        #      For better handling of this we must create more specialized
        #      shader that will handle this in more intelignet way
        if nthreads == 1 and not isinstance(self.props, dict):
            return self.props[0]
        return self.props

    def standalone(self):
        return self._standalone


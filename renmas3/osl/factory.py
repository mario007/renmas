
from .parser import Parser
from .cgen import CodeGenerator
from .arg import Argument, create_argument, ArgumentMap, ArgumentList

def _create_arg(a):
    if isinstance(a, Argument):
        return a
    elif (isinstance(a, list) or isinstance(a, tuple)) and len(a) == 2:
        name = a[0]
        value = a[1]
        arg = create_argument(name, value)
        return arg
    else:
        raise ValueError("Unknown data for creation of argument", a)

def create_argument_map(args):
    new_args = [_create_arg(a) for a in args]
    arg_map = ArgumentMap(new_args)
    return arg_map

def create_argument_list(args):
    new_args = [_create_arg(a) for a in args]
    arg_lst = ArgumentList(new_args)
    return arg_lst

def create_shader(name, source, args, input_args=[], shaders=[], func=False, functions=None):

    parser = Parser()
    cgen = CodeGenerator(name, args, input_args, shaders, func)
    parser.parse(source, cgen)
    shader = cgen.create_shader()
    return shader


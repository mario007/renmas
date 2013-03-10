
import inspect
from .parser import Parser
from .cgen import CodeGenerator
from .arg import Argument, ArgumentMap, ArgumentList
from .arg_fac import create_argument

def _create_arg(a, input_arg=False):
    if isinstance(a, Argument):
        return a
    elif (isinstance(a, list) or isinstance(a, tuple)) and len(a) == 2:
        name = a[0]
        value = a[1]
        if inspect.isclass(value):
            arg = create_argument(name, typ=value, input_arg=input_arg)
        else:
            arg = create_argument(name, value=value, input_arg=input_arg)
        return arg
    else:
        raise ValueError("Unknown data for creation of argument", a)

def arg_map(args):
    new_args = [_create_arg(a) for a in args]
    arg_map = ArgumentMap(new_args)
    return arg_map

def arg_list(args):
    new_args = [_create_arg(a, input_arg=True) for a in args]
    arg_lst = ArgumentList(new_args)
    return arg_lst

def create_shader(name, source, args, input_args=[], shaders=[], func=False):

    parser = Parser()
    cgen = CodeGenerator(name, args, input_args, shaders, func)
    parser.parse(source, cgen)
    shader = cgen.create_shader()
    return shader

def create_function(name, source, input_args=[], shaders=[]):

    parser = Parser()
    arg_map = ArgumentMap()
    cgen = CodeGenerator(name, arg_map, input_args, shaders, func=True)
    parser.parse(source, cgen)
    shader = cgen.create_shader()
    return shader



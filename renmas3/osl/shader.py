from .parser import Parser

class Shader:
    def __init__(self, args, input_args):
        pass

def create_shader(source, args, input_args=None, functions=None, shaders=None):

    parser = Parser()
    parser.parse(source, args)

    shader = Shader(args, input_args)
    return shader


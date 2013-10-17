
import os
from renlight.sdl import Loader, Shader, StructArg,\
    StructArgPtr, IntArg, FloatArg, register_struct
from renlight.sdl.args import ArgList

from .sample import Sample


class Tile2D:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


register_struct(Tile2D, 'Tile2D', fields=[('x', IntArg),
                ('y', IntArg), ('width', IntArg), ('height', IntArg)],
                factory=lambda: Tile2D(0, 0, 1, 1))


def create_tiles(width, height, nthreads):
    hp = int(float(height) / nthreads) + 1
    lst_tiles = []
    for k in range(0, height, hp):
        nh = hp
        if k > height - hp:
            nh = height - k
        lst_tiles.append(Tile2D(0, k, width, nh))

    return lst_tiles


class Sampler:
    def __init__(self):

        path = os.path.dirname(__file__)
        path = os.path.join(path, 'sam_shaders')
        self._loader = Loader([path])
        self.shader = None

        #default values
        self._width = 200
        self._height = 200
        self._pixel_size = 1.0
        self._pass_number = 1
        self._nthreads = 1

    def set_resolution(self, width, height):
        self._width = int(width)
        self._height = int(height)
        if self.shader is not None:
            self.shader.set_value('width', self._width)
            self.shader.set_value('height', self._height)

    def set_pass(self, n):
        self._pass_number = int(n)
        if self.shader is not None:
            self.shader.set_value('pass_number', self._pass_number)

    def set_pixel_size(self, size):
        self._pixel_size = float(size)
        if self.shader is not None:
            self.shader.set_value('pixel_size', self._pixel_size)

    def set_nthreads(self, n):
        self._nthreads = int(n)

    def load(self, shader_name):
        text = self._loader.load(shader_name, 'props.txt')
        #args = create_args(text)
        code = self._loader.load(shader_name, 'code.py')

        sample = Sample(0.0, 0.0, 0, 0, 0.0)
        func_args = [StructArgPtr('sample', sample)]

        args = [IntArg('width', self._width), IntArg('height', self._height),
                IntArg('pass_number', self._pass_number),
                FloatArg('pixel_size', self._pixel_size)]

        tiles = create_tiles(self._width, self._height, self._nthreads)
        targs = [StructArg('tile', tile) for tile in tiles]
        targ = ArgList('tile', targs)
        args.append(targ)
        curx_args = [IntArg('curx', 0) for tile in tiles]
        curx_arg = ArgList('curx', curx_args)
        args.append(curx_arg)
        cury_args = [IntArg('cury', tile.y) for tile in tiles]
        cury_arg = ArgList('cury', cury_args)
        args.append(cury_arg)
        endx_args = [IntArg('endx', tile.width) for tile in tiles]
        endx_arg = ArgList('endx', endx_args)
        args.append(endx_arg)
        endy_args = [IntArg('endy', tile.y + tile.height) for tile in tiles]
        endy_arg = ArgList('endy', endy_args)
        args.append(endy_arg)

        self.shader = Shader(code=code, args=args, name='generate_sample',
                             func_args=func_args, is_func=True)

    def compile(self):
        self.shader.compile()

    def prepare(self, runtimes):
        self.shader.prepare(runtimes)


import math
from tdasm import Runtime
from sdl import Shader, StructArgPtr, StructArg, ArgList, register_struct,\
    IntArg, FloatArg
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
    def __init__(self, width, height, pixelsize=1.0, nthreads=1):
        self._width = width
        self._height = height
        self._pixelsize = pixelsize
        self._nthreads = nthreads

        self._pass = 0
        self.shader = None

    @property
    def nthreads(self):
        return self._nthreads

    def get_resolution(self):
        return (self._width, self._height)

    def args(self):
        self._tiles = tiles = create_tiles(self._width, self._height, self._nthreads)

        n = self.nsamples()
        subx, suby = self._subpixel_location()

        args = [IntArg('width', self._width), IntArg('height', self._height),
                FloatArg('pixelsize', self._pixelsize), IntArg('nsamples', n),
                IntArg('npass', self._pass), IntArg('subx', subx),
                IntArg('suby', suby)]

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
        return args

    def create_shader(self):
        raise NotImplementedError()

    def compile(self, shaders=[]):
        if self.shader is not None:
            self.shader.compile(shaders)

    def prepare(self, runtimes):
        if self._nthreads != len(runtimes):
            raise ValueError("Expected %i runtimes and got %i!" %
                             (self._nthreads, len(runtimes)))

        if self.shader is not None:
            self.shader.prepare(runtimes)

    def reset(self):
        self._pass = 0
        self._update_shader_values()

    def _subpixel_location(self):
        n = self.nsamples()
        subx = self._pass // int(math.sqrt(n))
        suby = self._pass % int(math.sqrt(n))
        return (subx, suby)

    def _update_shader_values(self):
        if self.shader is not None:
            self.shader.set_value('npass', self._pass)
            subx, suby = self._subpixel_location()
            self.shader.set_value('subx', subx)
            self.shader.set_value('suby', suby)

            curx = [0 for tile in self._tiles]
            self.shader.set_value('curx', curx)

            cury = [tile.y for tile in self._tiles]
            self.shader.set_value('cury', cury)

    def increment_pass(self):
        self._pass += 1
        self._update_shader_values()

    def has_more_samples(self):
        if self._pass >= self.nsamples():
            return False
        return True

    def nsamples(self):
        return 1

    def prepare_standalone(self):

        runtimes = [Runtime()]
        self.compile()
        self.prepare(runtimes)

        code = """
ret = generate_sample(sample)
        """
        args = [StructArg('sample', Sample.factory()), IntArg('ret', 11)]
        self._standalone = Shader(code=code, args=args)
        self._standalone.compile([self.shader])
        self._standalone.prepare(runtimes)

    def generate_sample(self):

        self._standalone.execute()
        ret = self._standalone.get_value('ret')
        if ret == 0:
            return False
        sample = self._standalone.get_value('sample')
        return sample

    def output(self):
        txt = 'Sampler\n'
        txt += 'type = %s\n' % self.type_name()
        txt += 'width = %i\n' % self._width
        txt += 'height = %i\n' % self._height
        txt += 'nsamples = %i\n' % self.nsamples()
        txt += 'nthreads = %i\n' % self._nthreads
        txt += 'pixelsize = %f\n' % self._pixelsize 
        txt += 'End\n'
        return txt

    def type_name(self):
        raise NotImplementedError()


class SamplerGenerator():
    def __init__(self, sampler):
        self.sampler = sampler

        self.prepare_standalone()

    def prepare_standalone(self):

        self.sampler.create_shader()

        runtimes = [Runtime()]
        self.sampler.compile()
        self.sampler.prepare(runtimes)

        code = """
ret = generate_sample(sample)
        """
        args = [StructArg('sample', Sample.factory()), IntArg('ret', 11)]
        self._standalone = Shader(code=code, args=args)
        self._standalone.compile([self.sampler.shader])
        self._standalone.prepare(runtimes)

    def generate_sample(self):

        self._standalone.execute()
        ret = self._standalone.get_value('ret')
        if ret == 0:
            return False
        sample = self._standalone.get_value('sample')
        return sample


class RegularSampler(Sampler):
    def __init__(self, width=200, height=200, pixelsize=1.0, nthreads=1):
        super(RegularSampler, self).__init__(width, height, pixelsize, nthreads)

    def create_shader(self):
        code = """
if cury == endy:
    return 0

tmp = curx - width * 0.5 + 0.5
tmp2 = cury - height * 0.5 + 0.5

sample.x = pixelsize * tmp
sample.y = pixelsize * tmp2
sample.px = 0.5
sample.py = 0.5
sample.ix = curx
sample.iy = cury
sample.weight = 1.0

curx = curx + 1
if curx == endx:
    curx = tile.x
    cury = cury + 1
return 1
        """
        args = self.args()
        func_args = [StructArgPtr('sample', Sample.factory())]

        self.shader = Shader(code=code, args=args, name='generate_sample',
                             func_args=func_args, is_func=True)
        return self.shader

    def type_name(self):
        return 'regular'


class RandomSampler(Sampler):
    def __init__(self, width=200, height=200,
                 pixelsize=1.0, nthreads=1, nsamples=1):
        super(RandomSampler, self).__init__(width, height, pixelsize, nthreads)
        self._nsamples = nsamples

    def nsamples(self):
        return self._nsamples

    def create_shader(self):
        code = """
if cury == endy:
    return 0

rnds = random2()

tmp = curx - width * 0.5 + rnds[0]
tmp2 = cury - height * 0.5 + rnds[1]

sample.x = pixelsize * tmp
sample.y = pixelsize * tmp2
sample.px = rnds[0]
sample.py = rnds[1]
sample.ix = curx
sample.iy = cury
sample.weight = 1.0

curx = curx + 1
if curx == endx:
    curx = tile.x
    cury = cury + 1
return 1
        """
        args = self.args()
        func_args = [StructArgPtr('sample', Sample.factory())]

        self.shader = Shader(code=code, args=args, name='generate_sample',
                             func_args=func_args, is_func=True)
        return self.shader

    def type_name(self):
        return 'random'


class JitteredSampler(Sampler):
    def __init__(self, width=200, height=200,
                 pixelsize=1.0, nthreads=1, nsamples=1):
        super(JitteredSampler, self).__init__(width, height, pixelsize, nthreads)
        s = int(math.sqrt(nsamples))
        self._nsamples = s * s

    def nsamples(self):
        return self._nsamples

    def create_shader(self):
        code = """
if cury == endy:
    return 0

rnds = random2()
n = float(nsamples)
n = sqrt(n) 
px = (subx + rnds[0]) / n
py = (suby + rnds[1]) / n

tmp = curx - width * 0.5 + px
tmp2 = cury - height * 0.5 + py

sample.x = pixelsize * tmp
sample.y = pixelsize * tmp2
sample.px = px
sample.py = py
sample.ix = curx
sample.iy = cury
sample.weight = 1.0

curx = curx + 1
if curx == endx:
    curx = tile.x
    cury = cury + 1
return 1
        """
        args = self.args()
        func_args = [StructArgPtr('sample', Sample.factory())]

        self.shader = Shader(code=code, args=args, name='generate_sample',
                             func_args=func_args, is_func=True)
        return self.shader

    def type_name(self):
        return 'jittered'

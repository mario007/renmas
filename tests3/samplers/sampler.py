
import time
from tdasm import Runtime
from renmas3.base import Tile2D, BasicShader
from renmas3.samplers import Sample, create_regular_sampler

def extract(shader):
    ix = shader.get_value('sample.ix')
    iy = shader.get_value('sample.iy')
    x = shader.get_value('sample.x')
    y = shader.get_value('sample.y')
    ret = shader.get_value('ret')
    return ix, iy, x, y, ret

def test_values(sample, shader):
    ix, iy, x, y, ret = extract(shader)
    if sample is None and ret != 0:
        raise ValueError("Return value of generate sample is wrong", ret)
    if sample is None:
        return

    if ix != sample.ix:
        raise ValueError("ix is wrong! ix_py=%i, ix_asm=%i" % (sample.ix, ix))
    if iy != sample.iy:
        raise ValueError("iy is wrong! iy_py=%i, iy_asm=%i" % (sample.iy, iy))
    if x != sample.x:
        raise ValueError("x is wrong! x_py=%f, x_asm=%f" % (sample.x, x))
    if y != sample.y:
        raise ValueError("y is wrong! y_py=%f, y_asm=%f" % (sample.y, y))

def test_regular_sampler(width, height):
    sam = create_regular_sampler(width, height)
    runtime = Runtime()
    sam.prepare([runtime])
    tile = Tile2D(0, 0, width, height)
    sam.set_tile(tile)

    code = """
ret = generate_sample(sample)
    """
    sample = Sample(0.0, 0.0, 0, 0, 1.0)
    props = {'sample': sample, 'ret': 0}
    bas = BasicShader(code, None, props)
    bas.prepare([runtime], [sam.shader])

    while True:
        bas.execute()
        sample = sam.generate_sample()
        test_values(sample, bas.shader)
        if sample is None:
            break

def performance_regular_sampler(width, height):
    sam = create_regular_sampler(width, height)
    runtimes = [Runtime()]
    sam.prepare(runtimes)
    tile = Tile2D(0, 0, width, height)
    sam.set_tile(tile)

    code = """
ret = 1
nsamples = 0
while ret != 0:
    ret = generate_sample(sample)
    if ret == 0:
        break
    nsamples = nsamples + 1
    """
    sample = Sample(0.0, 0.0, 0, 0, 1.0)
    props = {'sample': sample, 'ret': 0, 'nsamples': 0}
    bas = BasicShader(code, None, props)
    bas.prepare(runtimes, [sam.shader])
    
    start = time.clock()
    bas.execute()
    end = time.clock()
    print("Exectution of generating %i samples took %f" % (bas.shader.get_value('nsamples') , end - start))

start = time.clock()
test_regular_sampler(100, 100)
end = time.clock()
print("Regular sampler working correctly. Time to verify took ", end - start)

performance_regular_sampler(2000, 2000)

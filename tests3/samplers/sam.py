
from tdasm import Runtime, Tdasm
import renmas2
import renmas2.core
import renmas2.samplers
import time

ASM_CODE = """
    #DATA
"""
ASM_CODE += renmas2.core.get_structs(('sample',)) + """
    sample sample1
    uint32 kraj 
    #CODE
    mov eax, sample1
    call get_sample
    mov dword [kraj], eax
    #END
"""

def get_sample(sampler, runtime, name):
    sample = sampler.get_sample() 
    print (sample)
    runtime.run(name)
    ds = runtime.get_datasection('test')
    ret = ds['kraj']
    if ret == 0:
        print(None)
    else:
        xyxy = ds['sample1.xyxy']
        ix = ds['sample1.ix']
        iy = ds['sample1.iy']
        print ('x=%f y=%f ix=%i iy=%i' % (xyxy[0], xyxy[1], ix, iy))

def regular_sampler():
    runtime = Runtime()
    sampler = renmas2.samplers.RegularSampler(2, 2, pixel=1.0)
    sampler.get_sample_asm([runtime], 'get_sample')
    tile = renmas2.core.Tile(0,0, 2, 2)
    tile.split(1)
    sampler.set_tile(tile)
    asm = Tdasm()
    mc = asm.assemble(ASM_CODE)
    runtime.load("test", mc)
    return (sampler, runtime, 'test')

def random_sampler():
    runtime = Runtime()
    width = 1
    height = 1 
    spp = 1
    sampler = renmas2.samplers.RandomSampler(width, height, spp=spp, pixel=1.0)
    sampler.get_sample_asm([runtime], 'get_sample')
    tile = renmas2.core.Tile(0,0, width, height)
    tile.split(1)
    sampler.set_tile(tile)
    asm = Tdasm()
    mc = asm.assemble(ASM_CODE)
    runtime.load("test", mc)

    nsamples = width * height * spp
    for x in range(nsamples):
        get_sample(sampler, runtime, "test")

    get_sample(sampler, runtime, "test")

random_sampler()

#sampler, runtime, name = regular_sampler()
#get_sample(sampler, runtime, name)







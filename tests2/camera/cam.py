
import time
from tdasm import Runtime, Tdasm
import renmas2
import renmas2.core
import renmas2.samplers
import renmas2.cameras

ASM_CODE = """
    #DATA
"""
ASM_CODE += renmas2.core.get_structs(('sample', 'ray')) + """
    sample sample1
    ray ray1
    uint32 kraj 
    #CODE
    mov eax, sample1
    call get_sample
    mov dword [kraj], eax
    mov eax, sample1
    mov ebx, ray1
    call get_ray
    #END
"""

cam = renmas2.cameras.Pinhole((2,3,4), (5,9,1))

width = 2
height = 2
sampler = renmas2.samplers.RegularSampler(width, height)
#sampler = renmas2.samplers.RandomSampler(width, height, n=1)

runtime = Runtime()
sampler.get_sample_asm([runtime], 'get_sample')
cam.ray_asm([runtime], 'get_ray')
asm = Tdasm()
mc = asm.assemble(ASM_CODE)
ds = runtime.load('test', mc)

tile = renmas2.core.Tile(0,0, width, height)
tile.split(1)
sampler.set_tile(tile)

start = time.clock()
while True:
    sample = sampler.get_sample()
    if sample is None: break
    ray = cam.ray(sample)
    print(ray)
    runtime.run('test')
    print(ds['ray1.origin'])
    print(ds['ray1.dir'])

end = time.clock()
print('Sample time = ', end - start)


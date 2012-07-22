
import time
from tdasm import Runtime
from renmas3.core.structures import SAMPLE, RAY
from renmas3.core import Tile
from renmas3.samplers import RegularSampler
from renmas3.cameras import Pinhole
from renmas3.core import ColorManager

ASM_CODE = """
    #DATA
"""
ASM_CODE += SAMPLE + RAY + """
    sample sample1
    ray ray1
    uint32 kraj 
    #CODE
    macro mov eax, sample1
    call get_sample
    mov dword [kraj], eax
    macro mov eax, sample1
    macro mov ebx, ray1
    call get_ray
    #END
"""

cam = Pinhole((2,3,4), (5,9,1))
mgr = ColorManager()

width = 2
height = 2
sampler = RegularSampler(width, height)

runtime = Runtime()
sampler.get_sample_asm([runtime], "get_sample", mgr.assembler)
cam.ray_asm([runtime], 'get_ray', mgr.assembler)
mc = mgr.assembler.assemble(ASM_CODE)
ds = runtime.load('test', mc)

tile = Tile(0,0, width, height)
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
    print('**********************')

end = time.clock()
print('Sample time = ', end - start)


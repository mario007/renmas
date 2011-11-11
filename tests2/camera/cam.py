
import renmas2
import renmas2.core
import renmas2.samplers
import renmas2.cameras
import time

cam = renmas2.cameras.Pinhole((2,3,4), (5,9,1))

#sampler = renmas2.samplers.RegularSampler(20000, 19660)
sampler = renmas2.samplers.RandomSampler(1024, 768, n=1)
#sampler.set_camera(cam)
sampler.set_ncore(1)
sampler.python_version(False)


time1 = time2 = 0
while True:
    start = time.clock()
    n = sampler.generate_samples()
    time1 += time.clock() - start
    if n == 0: break

print('Sample time = ', time1)


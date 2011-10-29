
import renmas2
import renmas2.core
import renmas2.samplers
import renmas2.cameras
import time

cam = renmas2.cameras.Pinhole((2,3,4), (5,9,1))
cam.set_ncore(1)
cam.python_version(False)

#sampler = renmas2.samplers.RegularSampler(20000, 1000)
sampler = renmas2.samplers.RandomSampler(1024, 768, n=1024)
sampler.set_ncore(1)
sampler.python_version(False)

time1 = time2 = 0
while True:
    start = time.clock()
    n = sampler.generate_samples()
    time1 += time.clock() - start

    if n == 0: break
    start = time.clock()
    cam.generate_rays(n, 0, sampler._sample_array)
    time2 += time.clock() - start

print('Sample time = ', time1)
print('Camera time = ', time2)
print('Combine time = ', time1 + time2)

for i in range(5):
    cam.show_ray(i)

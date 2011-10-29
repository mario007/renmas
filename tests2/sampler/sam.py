
import renmas2
import renmas2.core
import renmas2.samplers
import time


sampler = renmas2.samplers.RegularSampler(20000, 500, pixel=1.0)
sampler.set_ncore(2)
sampler.python_version(False)

rnd_sampler = renmas2.samplers.RandomSampler(1024, 768, n=128, pixel=1.0)


rnd_sampler.set_ncore(2)
rnd_sampler.python_version(False)

#rnd_sampler.generate_samples()

start = time.clock()
while True:
    n = rnd_sampler.generate_samples()
    #n = sampler.generate_samples()
    if n == 0: break


end = time.clock()
print(end-start)

for x in range(8):
    #sampler.show_sample(x)
    rnd_sampler.show_sample(x)




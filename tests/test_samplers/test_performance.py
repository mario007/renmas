
from renmas.samplers import RegularSampler, RandomSampler
from renmas.samplers import Sample 
import time


rnd = RandomSampler(10, 100, n=10)


sample = Sample()

start = time.clock()
while True:
    sam = rnd.get_sample(sample)
    if sam is None: break
end = time.clock()
print(end-start)

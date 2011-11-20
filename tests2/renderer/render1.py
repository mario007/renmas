
import time
import random
import renmas2
import renmas2.core
import renmas2.shapes

rnd = renmas2.Renderer()

def random_spheres(intersector, n):
    for i in range(n):
        center = renmas2.core.Vector3(0.0, 0.0, 0.0)
        radius = random.random() * 1.5 
        sph = renmas2.shapes.Sphere(center, radius, 0)
        intersector.add('sphere'+str(i), sph)

random_spheres(rnd._intersector, 20)
rnd.prepare()

start = time.clock()
while True:
    ret = rnd.render()
    if not ret: break

end = time.clock()
print(end-start)


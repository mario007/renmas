
import timeit
from tdasm import Tdasm, Runtime
import random
import renmas.utils as util
from renmas.shapes import Grid, isect_ray_scene
from renmas.core import Ray
import renmas.interface as mdl
from renmas.maths import Vector3

def generate_ray():
    x = random.random() * 10.0
    y = random.random() * 10.0
    z = random.random() * 10.0

    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    origin = Vector3(x, y, z)
    direction = Vector3(dir_x, dir_y, dir_z)
    direction.normalize()
    ray = Ray(origin, direction)
    return ray


if __name__ == "__main__":
    
    sph1 = mdl.create_random_sphere()
    #sph2 = mdl.create_random_sphere()
    #sph3 = mdl.create_random_sphere()

    for x in range(10000):
        sph3 = mdl.create_random_sphere()
    

    grid = Grid()
    t = timeit.Timer(lambda :grid.setup())
    print ("time", t.timeit(1))

    grid.setup()
    for n in range(100):
        ray = generate_ray()

        hp2 = isect_ray_scene(ray)
        hp = grid.intersect(ray)

        
        #print ("prvi grid", hp, hp2)
        if hp2 is not None:
            if hp is not None:
                if abs(hp.t - hp2.t) > 0.001:
                    print(hp.t, hp2.t)



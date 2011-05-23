
from tdasm import Tdasm, Runtime
from renmas.maths import Vector3
from renmas.shapes import Triangle 
from renmas.core import Ray
import random

def create_triangle():
    p0 = Vector3(1.1, 0.0, 0.0)    
    p1 = Vector3(4.0, 0.5, 0.2)
    p2 = Vector3(2.5, 4.3, 0.4)
    
    tr = Triangle(p0, p1, p2, 3)
    return tr


def create_ray():
    origin = Vector3(0.0, 0.0, 0.0) 
    direction = Vector3(8.8, 8.9, 8.7)
    direction.normalize()
    ray = Ray(origin, direction)
    return ray


def v4(v3):
    return (v3.x, v3.y, v3.z, 0.0)

if __name__ == "__main__":
    tr = create_triangle()
    ray = create_ray()
    pass

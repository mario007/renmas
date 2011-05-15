
import renmas.core
import renmas.shapes
import renmas.maths
import random

scene = renmas.core.scene


def create_random_sphere():
    x = random.random() * 10.0 - 5.0
    y = random.random() * 10.0 - 5.0
    z = random.random() * 10.0 - 5.0
    radius = random.random() * 0.15 
    
    v1 = renmas.maths.Vector3(x, y, z)
    sphere = renmas.shapes.Sphere(v1, radius, 99999)

    scene.shape_database.add_shape(sphere)
    return sphere


def create_random_plane():
    x = random.random() * 10.0
    y = random.random() * 10.0
    z = random.random() * 10.0

    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    point = renmas.maths.Vector3(x, y, z)
    normal = renmas.maths.Vector3(dir_x, dir_y, dir_z)
    normal.normalize()

    plane = renmas.shapes.Plane(point, normal, 99998)
    scene.shape_database.add_shape(plane)
    return plane


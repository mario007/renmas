
import renmas
import renmas.maths
import renmas.shapes
import renmas.camera
import random

scene = renmas.scene
geometry = renmas.geometry

def pinhole_camera(eye, lookat, distance=100):
    ex, ey, ez = eye
    lx, ly, lz = lookat
    eye = renmas.maths.Vector3(float(ex), float(ey), float(ez))
    lookat = renmas.maths.Vector3(float(lx), float(ly), float(lz))
    cam = renmas.camera.PinholeCamera(eye, lookat, float(distance))
    return cam
    
def create_sphere(x, y, z, radius):
    v1 = renmas.maths.Vector3(float(x), float(y), float(z))
    sphere = renmas.shapes.Sphere(v1, float(radius), 99999)

    geometry.add_shape(sphere)
    return sphere


def random_sphere():
    x = random.random() * 10.0 - 5.0
    y = random.random() * 10.0 - 5.0
    z = random.random() * 10.0 - 5.0
    radius = random.random() * 1.50 
    
    v1 = renmas.maths.Vector3(x, y, z)
    sphere = renmas.shapes.Sphere(v1, radius, 99999)

    geometry.add_shape(sphere)
    return sphere

def random_ray():
    x = random.random() * 10.0 - 5.0
    y = random.random() * 10.0 - 5.0
    z = random.random() * 10.0 - 5.0

    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    origin = renmas.maths.Vector3(x, y, z)
    direction = renmas.maths.Vector3(dir_x, dir_y, dir_z)
    direction.normalize()
    ray = renmas.core.Ray(origin, direction)
    return ray


def random_plane():
    x = random.random() * 10.0
    y = random.random() * 10.0
    z = random.random() * 10.0

    dir_x = random.random() * 10.0 - 5.0
    dir_y = random.random() * 10.0 - 5.0
    dir_z = random.random() * 10.0 - 5.0

    point = renmas.maths.Vector3(x, y, z)
    normal = renmas.maths.Vector3(dir_x, dir_y, dir_z)
    normal.normalize()

    plane = renmas.shapes.Plane(point, normal, 99999)
    geometry.add_shape(plane)
    return plane

def random_triangle():
    p0 = renmas.maths.Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
    p1 = renmas.maths.Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
    p2 = renmas.maths.Vector3(random.random()*10.0-5.0, random.random()*10-5.0, random.random()*10-5.0)    
    tri = renmas.shapes.Triangle(p0, p1, p2, 99999)
    geometry.add_shape(tri)
    return tri

def lst_shapes():
    return geometry.shapes()

def dyn_arrays():
    geometry.create_asm_arrays()
    return geometry.asm_shapes


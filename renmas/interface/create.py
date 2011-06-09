
import renmas
import renmas.maths
import renmas.shapes
import renmas.camera
import renmas.materials
import renmas.lights
import renmas.samplers
import random

scene = renmas.scene
geometry = renmas.geometry
mat_db = renmas.mat_db
light_db = renmas.light_db

sampler = None
camera = None
film = None

def create_triangle(p0, p1, p2, mat_idx):
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    p0 = renmas.maths.Vector3(float(x0), float(y0), float(z0))
    p1 = renmas.maths.Vector3(float(x1), float(y1), float(z1))
    p2 = renmas.maths.Vector3(float(x2), float(y2), float(z2))
    tri = renmas.shapes.Triangle(p0, p1, p2, mat_idx)

    geometry.add_shape(tri)
    return tri
    
def create_spectrum(r, g, b):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    return spectrum

def lst_lights():
    return light_db.get_lights()

def create_point_light(name, pos, spectrum):
    x, y, z = pos
    r, g, b = spectrum
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    pos = renmas.maths.Vector3(float(x), float(y), float(z))
    plight = renmas.lights.PointLight(pos, spectrum) 
    light_db.add_light(plight)
    return plight

def create_lambertian(name, r, g, b):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    lamb = renmas.materials.Lambertian(spectrum)
    mat = renmas.materials.Material()
    mat.add_component(lamb)
    mat_db.add_material(name, mat) 
    return mat

def create_phong(name, r, g, b, e):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    lamb = renmas.materials.Lambertian(spectrum)
    phong = renmas.materials.Phong(spectrum, float(e))

    mat = renmas.materials.Material()
    mat.add_component(lamb)
    mat.add_component(phong)
    mat_db.add_material(name, mat)
    return mat

def create_oren(name, r, g, b, alpha):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    oren = renmas.materials.Oren_Nayar(spectrum, float(alpha))

    mat = renmas.materials.Material()
    mat.add_component(oren)
    mat_db.add_material(name, mat)
    return mat

def create_oren_phong(name, r, g, b, alpha, e):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    oren = renmas.materials.Oren_Nayar(spectrum, float(alpha))
    phong = renmas.materials.Phong(spectrum, float(e))

    mat = renmas.materials.Material()
    mat.add_component(oren)
    mat.add_component(phong)
    mat_db.add_material(name, mat)
    return mat

def get_material(idx):
    return mat_db.material_idx(idx)

def get_mat_idx(name):
    return mat_db.get_idx(name)

def pinhole_camera(eye, lookat, distance=100):
    ex, ey, ez = eye
    lx, ly, lz = lookat
    eye = renmas.maths.Vector3(float(ex), float(ey), float(ez))
    lookat = renmas.maths.Vector3(float(lx), float(ly), float(lz))
    cam = renmas.camera.PinholeCamera(eye, lookat, float(distance))
    global camera
    camera = cam
    return cam
    
def create_sphere(x, y, z, radius, mat=99999):
    v1 = renmas.maths.Vector3(float(x), float(y), float(z))
    sphere = renmas.shapes.Sphere(v1, float(radius), mat)

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

def get_tiles(width, height, nsamples):
    # TODO - implement later smarter version to include number os sample and assembly version
    w = 50
    h = 50 
    
    sx = 0
    sy = 0
    xcoords = []
    ycoords = []
    tiles = []
    while sx < width:
        xcoords.append(sx)
        sx += w
    last_w = width - (sx - w) 
    while sy < height:
        ycoords.append(sy)
        sy += h
    last_h = height - (sy - h)

    for i in xcoords:
        for j in ycoords:
            tw = w
            th = h
            if i == xcoords[-1]:
                tw = last_w
            if j == ycoords[-1]:
                th = last_h
            tiles.append((i, j, tw, th))

    #print(xcoords)
    #print(ycoords)
    #print(last_w, last_h)
    #print(tiles)
    return tiles

def create_random_sampler(width, height, nsamples):
    sam = renmas.samplers.RandomSampler(width, height, n=nsamples)
    global sampler
    sampler = sam 
    return sam

def get_sampler():
    return sampler

def get_camera():
    return camera

def create_film(width, height, nsamples):
    fil = renmas.core.Film(width, height, nsamples)
    global film
    film = fil
    return fil

def get_film():
    return film


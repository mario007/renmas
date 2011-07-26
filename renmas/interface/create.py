
import renmas
import renmas.maths
import renmas.camera
import renmas.materials
import renmas.shapes
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

def create_spectrum(r, g, b):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    return spectrum

def lst_lights():
    return light_db.get_lights()

def lst_materials():
    return mat_db.get_materials()


def create_lambertian(name, r, g, b):
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    lamb = renmas.materials.LambertianBRDF(spectrum)
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

def isect_shapes():
    return geometry.isect_shapes()

def prepare_for_rendering():
    geometry.prepare_shapes()

def dyn_arrays():
    arr = geometry.dyn_arrays_for_isect()
    return arr

    return geometry.dyn_arrays

def get_tiles(width, height, nsamples):
    # TODO - implement later smarter version to include number os sample and assembly version
    # different size of tile for python and assembler
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


def create_material(props):
    name = props.get("name", "")
    sampling = props.get("sampling", None)

    mat = renmas.materials.Material()
    if sampling is not None:
        if sampling == "hemisphere_cos":
            sampling = renmas.materials.HemisphereCos()
            mat.add_sampling(sampling)
    mat_db.add_material(name, mat) 
    return mat

def add_brdf(material_name, props):
    # props is dict with properties
    brdf_name = props.get("type", "")
    if brdf_name == "lambertian":
        #he has reflectence properties for three channels
        r, g, b = props["R"]
        k = props.get("k", None)
        spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
        lamb = renmas.materials.LambertianBRDF(spectrum, k)
        mat = mat_db.mat(material_name) 
        mat.add_component(lamb)
    elif brdf_name == "constant":
        r, g, b = props["R"]
        k = props.get("k", None)
        spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
        c = renmas.materials.ConstantBRDF(spectrum, k)
        mat = mat_db.mat(material_name) 
        mat.add_component(c)
    elif brdf_name == "phong":
        r, g, b = props["R"]
        e = props["e"]
        k = props.get("k", None)
        spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
        c = renmas.materials.PhongBRDF(spectrum, float(e), k)
        mat = mat_db.mat(material_name) 
        mat.add_component(c)
    else:
        raise ValueError("unknown brdf name")

def create_random_sampler(props):
    width = props["width"]
    height = props["height"]
    nsamples = props.get("nsamples", 1)
    pixel_size = props.get("pixel", 1.0)
    sam = renmas.samplers.RandomSampler(width, height, n=nsamples, pixel=float(pixel_size))
    global sampler
    sampler = sam 
    return sam

def create_regular_sampler(props):
    width = props["width"]
    height = props["height"]
    pixel_size = props.get("pixel", 1.0)
    sam = renmas.samplers.RegularSampler(width, height, pixel=float(pixel_size))
    global sampler
    sampler = sam 
    return sam

def create_sampler(props):
    
    typ_sampler = props.get("type", "")
    if typ_sampler == "random":
        return create_random_sampler(props)
    elif typ_sampler == "regular":
        return create_regular_sampler(props)
    else:
        raise ValueError("unknown type of sampler")

def create_pinhole_camera(props):
    ex, ey, ez = props["eye"] 
    lx, ly, lz = props["lookat"] 
    distance = props.get("distance", 100)

    eye = renmas.maths.Vector3(float(ex), float(ey), float(ez))
    lookat = renmas.maths.Vector3(float(lx), float(ly), float(lz))
    cam = renmas.camera.PinholeCamera(eye, lookat, float(distance))
    global camera
    camera = cam
    return cam

def create_camera(props):

    typ_camera = props.get("type", "")
    if typ_camera =="pinhole":
        return create_pinhole_camera(props)
    else:
        raise ValueError("unknown type of camera")

def create_film(props):
    width = props["width"]
    height = props["height"]
    nsamples = props.get("nsamples", 1)

    fil = renmas.core.Film(width, height, nsamples)
    global film
    film = fil
    return fil

def create_point_light(props):
    name = props.get("name", "unknown")
    x, y, z = props["position"]
    r, g, b, = props["spectrum"]

    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    pos = renmas.maths.Vector3(float(x), float(y), float(z))
    plight = renmas.lights.PointLight(pos, spectrum) 
    light_db.add_light(plight)
    return plight

def create_area_light(props):
    name = props.get("name", "unknown")
    r, g, b, = props["spectrum"]
    spectrum = renmas.core.Spectrum(float(r), float(g), float(b))
    

    x, y, z = props["p"] 
    nx, ny, nz = props["normal"] 
    eda_x, eda_y, eda_z = props["edge_a"] 
    edb_x, edb_y, edb_z = props["edge_b"] 

    p = renmas.maths.Vector3(float(x), float(y), float(z))
    n = renmas.maths.Vector3(float(nx), float(ny), float(nz))
    edge_a = renmas.maths.Vector3(float(eda_x), float(eda_y), float(eda_z))
    edge_b = renmas.maths.Vector3(float(edb_x), float(edb_y), float(edb_z))

    rect = renmas.shapes.Rectangle(p, edge_a, edge_b, n,  99999)
    a_light = renmas.lights.AreaLight(spectrum, rect)
    light_db.add_light(a_light)

    return a_light

def create_light(props):
    typ_light = props.get("type", "")
    if typ_light == "point":
        return create_point_light(props)
    elif typ_light == "area":
        return create_area_light(props)
    else:
        raise ValueError("unknown type of light")

def create_sphere(props):
    x, y, z = props["position"]
    radius = props["radius"]
    mat_name = props["material"]

    name = props.get("name", "Sphere" + str(renmas.utils.unique()))
    idx = get_mat_idx(mat_name)

    v1 = renmas.maths.Vector3(float(x), float(y), float(z))
    sphere = renmas.shapes.Sphere(v1, float(radius), idx)

    geometry.add_shape(name, sphere)
    return sphere

def create_triangle(props):
    x0, y0, z0 = props["p0"] 
    x1, y1, z1 = props["p1"] 
    x2, y2, z2 = props["p2"] 
    mat_name = props["material"]
    mat_idx = get_mat_idx(mat_name)

    name = props.get("name", "Triangle" + str(renmas.utils.unique()))

    p0 = renmas.maths.Vector3(float(x0), float(y0), float(z0))
    p1 = renmas.maths.Vector3(float(x1), float(y1), float(z1))
    p2 = renmas.maths.Vector3(float(x2), float(y2), float(z2))
    tri = renmas.shapes.Triangle(p0, p1, p2, mat_idx)

    geometry.add_shape(name, tri)
    return tri

def create_rectangle(props):
    x, y, z = props["p"] 
    nx, ny, nz = props["normal"] 
    eda_x, eda_y, eda_z = props["edge_a"] 
    edb_x, edb_y, edb_z = props["edge_b"] 
    mat_name = props["material"]
    mat_idx = get_mat_idx(mat_name)

    name = props.get("name", "Rectangle" + str(renmas.utils.unique()))

    p = renmas.maths.Vector3(float(x), float(y), float(z))
    n = renmas.maths.Vector3(float(nx), float(ny), float(nz))
    edge_a = renmas.maths.Vector3(float(eda_x), float(eda_y), float(eda_z))
    edge_b = renmas.maths.Vector3(float(edb_x), float(edb_y), float(edb_z))

    rect = renmas.shapes.Rectangle(p, edge_a, edge_b, n,  mat_idx)
    geometry.add_shape(name, rect)
    return rect

def create_mesh(props):
    mat_name = props["material"]
    mat_idx = get_mat_idx(mat_name)
    name = props.get("name", "Mesh" + str(renmas.utils.unique()))
    mesh = renmas.shapes.Mesh3D(mat_idx)

    fnames = props.get("resource", None)
    if fnames:
        for fname in fnames:
            mesh.load_ply(fname)
    scale = props.get("scale", None)
    if scale:
        mesh.scale(scale[0], scale[1], scale[2])
        mesh.calculate_bbox()

    translate = props.get("translate", None)
    if translate:
        mesh.translate(translate[0], translate[1], translate[2])
        mesh.calculate_bbox()

    mesh.prepare_isect()

    geometry.add_shape(name, mesh)
    return mesh


def create_shape(props):
    type_shape = props.get("type", "")
    if type_shape == "sphere":
        return create_sphere(props)
    elif type_shape == "triangle":
        return create_triangle(props)
    elif type_shape == "rectangle":
        return create_rectangle(props)
    elif type_shape == "mesh":
        return create_mesh(props)
    else:
        raise ValueError("unknown type of shape")

def get_sampler():
    return sampler

def get_camera():
    return camera

def get_film():
    return film

def tiles():
    if sampler is None: return None

    width = sampler.width
    height = sampler.height
    nsamples = sampler.nsamples()
    
    return get_tiles(width, height, nsamples)


#  list of objects must be in shape database

def objfunc_array(lst_shapes, runtime):

    addr = []
    for shape in lst_shapes:
        objadr = geometry.obj_address(shape=shape)
        addr.append(objadr)

        if not runtime.global_exists(shape.isect_name()):
            shape.isect_asm(runtime, shape.isect_name())
        lbl_addr = runtime.address_label(shape.isect_name())
        addr.append(lbl_addr)

    return tuple(addr)


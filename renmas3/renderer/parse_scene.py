import time
import math
import os.path
from ..base import Vector3, Spectrum, load_image, ImagePRGBA
from ..samplers import RegularSampler, RandomSampler
from ..cameras import create_perspective_camera
from ..shapes import Sphere, Triangle, Rectangle, load_meshes_from_file

from .light import Light
from .lights import create_point_illuminate
from .mat import Material
from .materials import create_lambertian_brdf, create_lambertian_sample
from .materials import create_lambertian_pdf, create_lambertian_emission
from .parse_matlib import parse_matlib
from .sunsky import SunSky
from .env_light import EnvLight

def _set_lat_long_coords(u, v):
    theta = u * math.pi
    phi = v * 2 * math.pi
    x = math.sin(theta) * math.cos(phi)
    y = math.cos(theta)
    z = -math.sin(theta) * math.sin(phi)
    return x, y, z

def _get_mirror_ball_pixel_coord(x, y, z):
    u = x / math.sqrt(2 * (1 + z))
    v = y / math.sqrt(2 * (1 + z))
    return u, v

def conv_angular_to_ll(img):
    width, height = img.size()
    new_img = ImagePRGBA(width*2, height)
    for j in range(height):
        for i in range(width * 2):
            x, y, z = _set_lat_long_coords(1 - j / float(height - 1), i / float(width * 2 - 1))
            u, v = _get_mirror_ball_pixel_coord(x, y, z)
            #convert to pixel coordiantes
            u = (u + 1) * 0.5 * width
            v = (v + 1) * 0.5 * height
            r, g, b, a = img.get_pixel(int(u), int(v))
            new_img.set_pixel(i, j, r, g, b, a)
    return new_img

def _parse_line(line):
    keyword, vals = line.split('=')
    vals = vals.split(',')
    return keyword.strip(), vals

def _extract_values(fobj):
    values = {}

    for line in fobj:
        line = line.strip()
        if line == "" or line[0] == '#': #skip blank lines and comments
            continue
        if line.lower()  == 'end':
            break
        key, vals = _parse_line(line)
        values[key] = vals
    return values

def _parse_options(fobj, project):
    values = _extract_values(fobj)

    #NOTE keywords are expected to be in lower case!!!
    width = int(values['width'][0])
    height = int(values['height'][0])
    typ = 'regular'
    if 'sampler_type' in values:
        typ = values['sampler_type'][0].strip().lower()

    if typ == 'regular':
        if 'pixel_size' in values:
            pixel_size = float(values['pixel_size'][0])
            sampler = RegularSampler(width, height, pixel_size=pixel_size)
        else:
            sampler = RegularSampler(width, height)
        project.sampler = sampler
    elif typ == 'random':
        nsamples = 1
        if 'nsamples' in values:
            nsamples = int(values['nsamples'][0])
        if 'pixel_size' in values:
            pixel_size = float(values['pixel_size'][0])
            sampler = RandomSampler(width, height, nsamples=nsamples, pixel_size=pixel_size)
        else:
            sampler = RandomSampler(width, height, nsamples=nsamples)
        project.sampler = sampler

    if 'nthreads' in values:
        project.nthreads = int(values['nthreads'][0])


def _parse_camera(fobj, project):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this
    eye = values['eye']  
    eye = Vector3(float(eye[0]), float(eye[1]), float(eye[2]))
    lookat = values['lookat']  
    lookat = Vector3(float(lookat[0]), float(lookat[1]), float(lookat[2]))
    distance = float(values['distance'][0])

    typ = 'perspective'
    if 'type' in values:
        typ = values['type'][0].strip().lower()

    if typ == 'perspective':
        camera = create_perspective_camera(eye, lookat, distance)
        project.camera = camera
    else:
        raise ValueError("Unknown camera")

def _parse_shape(fobj, project):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this

    if 'type' not in values:
        raise ValueError("Type attribut is missing")
    typ = values['type'][0].strip().lower()
    if 'name' in values:
        name = values['name'][0].strip()
    else:
        name = None
    if typ == 'sphere':
        radius = float(values['radius'][0])
        o = values['origin']
        origin = Vector3(float(o[0]), float(o[1]), float(o[2]))
        sphere = Sphere(origin, radius)
        project.shapes.add(name, sphere)
    elif typ == 'triangle':
        p0 = values['p0']
        p0 = Vector3(float(p0[0]), float(p0[1]), float(p0[2]))
        p1 = values['p1']
        p1 = Vector3(float(p1[0]), float(p1[1]), float(p1[2]))
        p2 = values['p2']
        p2 = Vector3(float(p2[0]), float(p2[1]), float(p2[2]))
        tri = Triangle(p0, p1, p2)
        project.shapes.add(name, tri)
    elif typ == 'rectangle':
        p = values['p']
        p = Vector3(float(p[0]), float(p[1]), float(p[2]))
        e1 = values['edge_a']
        e1 = Vector3(float(e1[0]), float(e1[1]), float(e1[2]))
        e2 = values['edge_b']
        e2 = Vector3(float(e2[0]), float(e2[1]), float(e2[2]))
        n = values['normal']
        n = Vector3(float(n[0]), float(n[1]), float(n[2]))
        rect = Rectangle(p, e1, e2, normal=n)
        project.shapes.add(name, rect)
    elif typ == 'mesh':
        directory = os.path.dirname(os.path.abspath(fobj.name))
        fname = values['fname'][0].strip()
        filename = os.path.join(directory, fname)

        meshes = load_meshes_from_file(filename, project=project, material_loader=lambda mlib_fobj: parse_matlib(mlib_fobj, project))
        for name, mesh in meshes.items():
            if 'translate' in values:
                dx = float(values['translate'][0])
                dy = float(values['translate'][1])
                dz = float(values['translate'][2])
                mesh.translate(dx, dy, dz)
            if 'scale' in values:
                sx = float(values['scale'][0])
                sy = float(values['scale'][1])
                sz = float(values['scale'][2])
                mesh.scale(sx, sy, sz)
            mesh.prepare(performanse=False)
            project.shapes.add(name, mesh)
            if 'material' in values:
                mat_name = values['material'][0].strip()
                project.set_material(name, mat_name)
        return
    else:
        raise ValueError("Unsuported type of shape!", typ)
    if 'material' in values and name is not None:
        mat_name = values['material'][0].strip()
        project.set_material(name, mat_name)

def _gen_name(obj, prefix):
    return prefix + str(id(obj))

def _parse_light(fobj, project):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this
    if 'type' not in values:
        raise ValueError("Type attribut is missing")
    typ = values['type'][0].strip().lower()
    if typ == 'pointlight':
        o = values['position']
        position = Vector3(float(o[0]), float(o[1]), float(o[2]))
        i = values['intesity']
        if len(i) == 3: #assume RGB TODO spectrums
            r, g, b = float(i[0]), float(i[1]), float(i[2])
        else:
            raise ValueError("Spectrum values not yet implemented")
        intesity = project.col_mgr.create_spectrum((r, g, b), illum=True)
        sh = create_point_illuminate(project.col_mgr, position, intesity)
        light = Light(illuminate=sh)
        project.lgt_mgr.add(_gen_name(light, 'light'), light)
    elif typ == 'sunsky':
        sun_sky = SunSky(project.col_mgr)
        project.lgt_mgr.add('sun1', sun_sky)
    elif typ == 'envlight':
        directory = os.path.dirname(os.path.abspath(fobj.name))
        fname = values['fname'][0].strip()
        filename = os.path.join(directory, fname)
        img = load_image(filename)
        #img = conv_angular_to_ll(img)
        env_lgt = EnvLight(img, project.col_mgr)
        project.lgt_mgr.add('env1', env_lgt)
    else:
        raise ValueError("Unsuported type of light!", typ)

def _parse_material(fobj, project):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this
    name = values['name'][0].strip()
    typ = values['type'][0].strip().lower()
    props = project.create_props(typ)
    for key, value in values.items():
        if key == 'name' or key == 'type':
            continue
        if key not in props:
            raise ValueError('Property %s not in props of material' % key)

        if isinstance(props[key], int):
            props[key] = int(values[key][0])
        elif isinstance(props[key], float):
            props[key] = float(values[key][0])
        elif isinstance(props[key], Spectrum):
            #assume RGB spectrum TODO xyz, sampled etc...
            r, g, b = float(values[key][0]), float(values[key][1]), float(values[key][2])
            props[key] =  project.col_mgr.create_spectrum((r, g, b))

    mat = project.create_material(name, typ, props)
    project.mat_mgr.add(name, mat)

def _parse_material1(fobj, project):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this
    name = values['name'][0].strip()
    typ = values['type'][0].strip().lower()
    if typ == 'lambertian':
        i = values['diffuse']
        if len(i) == 3: #assume RGB TODO spectrums
            r, g, b = float(i[0]), float(i[1]), float(i[2])
        else:
            raise ValueError("Spectrum values not yet implemented")
        diffuse = project.col_mgr.create_spectrum((r, g, b))
        sh = create_lambertian_brdf(project.col_mgr, diffuse)
        sample = create_lambertian_sample(project.col_mgr)
        pdf = create_lambertian_pdf(project.col_mgr)

        em_sh = None
        if 'emission' in values:
            i = values['emission']
            if len(i) == 3: #assume RGB TODO spectrums
                r, g, b = float(i[0]), float(i[1]), float(i[2])
            else:
                raise ValueError("Spectrum values not yet implemented")
            emission = project.col_mgr.create_spectrum((r, g, b))
            em_sh = create_lambertian_emission(project.col_mgr, emission)

        new_mat = project.create_material(name, typ)

        mat = Material(bsdf=sh, sample=sample, pdf=pdf, emission=em_sh)
        project.mat_mgr.add(name, mat)

def parse_scene(fobj, project):
    for line in fobj:
        line = line.strip()
        if line == "" or line[0] == '#': #skip blank lines and comments
            continue
        if line.lower() == "options":
            _parse_options(fobj, project)
        elif line.lower() == "camera":
            _parse_camera(fobj, project)
        elif line.lower() == "shape":
            _parse_shape(fobj, project)
        elif line.lower() == "light":
            _parse_light(fobj, project)
        elif line.lower() == "material":
            _parse_material(fobj, project)
        else:
            raise ValueError("Unknown keyword in scene file!", line)


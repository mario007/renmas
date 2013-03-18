
from ..base import Vector3
from ..samplers import RegularSampler
from ..cameras import create_perspective_camera
from ..shapes import Sphere

from .light import Light
from .lights import create_point_illuminate
from .mat import Material
from .materials import create_lambertian_brdf

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
            sampler = RegularSampler(width, height, pixel_size)
        else:
            sampler = RegularSampler(width, height)
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
    name = values['name'][0].strip()
    if typ == 'sphere':
        radius = float(values['radius'][0])
        o = values['origin']
        origin = Vector3(float(o[0]), float(o[1]), float(o[2]))
        sphere = Sphere(origin, radius)
        project.shapes.add(name, sphere)
    else:
        raise ValueError("Unsuported type of shape!", typ)
    if 'material' in values:
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
    else:
        raise ValueError("Unsuported type of light!", typ)

def _parse_material(fobj, project):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this
    typ = values['type'][0].strip().lower()
    if typ == 'lambertian':
        i = values['diffuse']
        if len(i) == 3: #assume RGB TODO spectrums
            r, g, b = float(i[0]), float(i[1]), float(i[2])
        else:
            raise ValueError("Spectrum values not yet implemented")
        diffuse = project.col_mgr.create_spectrum((r, g, b))
        name = values['name'][0].strip()
        sh = create_lambertian_brdf(project.col_mgr, diffuse)
        mat = Material(brdf=sh)
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


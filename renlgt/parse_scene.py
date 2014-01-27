
from sdl import Vector3
from .camera import Camera
from .sphere import Sphere

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

def _parse_camera(fobj, renderer):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this

    eye = values['eye']  
    eye = Vector3(float(eye[0]), float(eye[1]), float(eye[2]))
    lookat = values['lookat']  
    lookat = Vector3(float(lookat[0]), float(lookat[1]), float(lookat[2]))
    distance = float(values['distance'][0])

    camera = Camera(eye=eye, lookat=lookat, distance=distance)
    typ = values['type'][0].strip().lower()
    camera.load(typ)

    #TODO - shader public parameters
    renderer.camera = camera


def _parse_shape(fobj, renderer):
    values = _extract_values(fobj)
    #NOTE keywords are expected to be in lower case!!! Improve this

    if 'type' not in values:
        raise ValueError("Type attribut for shape is missing")
    typ = values['type'][0].strip().lower()
    if typ == 'sphere':
        name = values['name'][0].strip()
        radius = float(values['radius'][0])
        o = values['origin']
        origin = Vector3(float(o[0]), float(o[1]), float(o[2]))
        sphere = Sphere(origin, radius, mat_idx=0)
        renderer.shapes.add(name, sphere)
    else:
        raise ValueError("Unsuported type of shape!", typ)


def import_scene(filename, renderer):
    #TODO file exists
    fobj = open(filename)
    for line in fobj:
        line = line.strip()
        if line == "" or line[0] == '#': #skip blank lines and comments
            continue
        if line.lower() == 'camera':
            _parse_camera(fobj, renderer)
        elif line.lower() == 'shape':
            _parse_shape(fobj, renderer)
        else:
            raise ValueError("Unknown keyword in scene file!", line)


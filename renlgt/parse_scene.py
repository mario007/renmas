
from sdl import Vector3, RGBSpectrum, SampledSpectrum
from .camera import Camera
from .sphere import Sphere
from .light import GeneralLight
from .material import Material
from .triangle import FlatTriangle


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

def _value_factory(old_val, val, sam_mgr, light=False):
    
    if isinstance(old_val, Vector3):
        return Vector3(float(val[0]), float(val[1]), float(val[2]))
    elif isinstance(old_val, RGBSpectrum):
        #TODO parsing of spectrum values from file
        return RGBSpectrum(float(val[0]), float(val[1]), float(val[2]))
    elif isinstance(old_val, SampledSpectrum):
        #TODO parsing of spectrum values from file
        s = RGBSpectrum(float(val[0]), float(val[1]), float(val[2]))
        return sam_mgr.rgb_to_sampled(s, illum=light)
    else:
        raise ValueError("Unknown type ", old_val)


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

def _parse_light(fobj, renderer):
    values = _extract_values(fobj)
    if 'type' not in values:
        raise ValueError("Type attribute for light is missing")
    typ = values['type'][0].strip()
    light = GeneralLight()
    light.load(typ, renderer.sam_mgr, renderer.spectral)
    del values['type']
    name = 'light_%i' % id(light)
    if 'name' in values:
        name = values['name'][0].strip()
        del values['name']
    for key, val in values.items():
        old_val = light.get_value(key)
        new_val = _value_factory(old_val, val, renderer.sam_mgr)
        light.set_value(key, new_val)
    renderer.lights.add(name, light)

def _parse_material(fobj, renderer):
    values = _extract_values(fobj)
    if 'type' not in values:
        raise ValueError("Type attribute for light is missing")
    typ = values['type'][0].strip()
    mat = Material()
    mat.load(typ, renderer.sam_mgr, renderer.spectral)
    if 'name' not in values:
        raise ValueError("Material name is missing")
    name = values['name'][0].strip()
    del values['type']
    del values['name']
    for key, val in values.items():
        old_val = mat.get_value(key)
        new_val = _value_factory(old_val, val, renderer.sam_mgr)
        mat.set_value(key, new_val)
    renderer.materials.add(name, mat)


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
        mat_name = values['material'][0].strip()
        mat_idx = renderer.materials.index(mat_name)
        sphere = Sphere(origin, radius, mat_idx=mat_idx)
        renderer.shapes.add(name, sphere)
    elif typ == 'flattriangle':
        name = values['name'][0].strip()
        p = values['p0']
        p0 = Vector3(float(p[0]), float(p[1]), float(p[2]))
        p = values['p1']
        p1 = Vector3(float(p[0]), float(p[1]), float(p[2]))
        p = values['p2']
        p2 = Vector3(float(p[0]), float(p[1]), float(p[2]))
        mat_name = values['material'][0].strip()
        mat_idx = renderer.materials.index(mat_name)
        flat = FlatTriangle(p0, p1, p2, mat_idx)
        renderer.shapes.add(name, flat)
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
        elif line.lower() == 'light':
            _parse_light(fobj, renderer)
        elif line.lower() == 'material':
            _parse_material(fobj, renderer)
        elif line.lower() == 'shape':
            _parse_shape(fobj, renderer)
        else:
            raise ValueError("Unknown keyword in scene file!", line)


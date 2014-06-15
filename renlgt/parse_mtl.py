
import os.path
from imldr.load_image import load_image
from sdl import RGBSpectrum
from .material import Material

#Ka 0.0435 0.0435 0.0435
#Kd 0.1086 0.1086 0.1086
#Ks 0.0000 0.0000 0.0000
#Ns 10.0000
#Ni 1.6000
#d 1.0000
# Tr 0.0000
# Tf 1.0000 1.0000 1.0000 
#illum 2
#map_Ka Maps\DetMoldura_04_Color.jpg
#map_Kd Maps\DetMoldura_04_Color.jpg
#map_d Maps\aglaonema_leaf.tga

def _zero_spectrum(vals):
    r, g, b = float(vals[0]), float(vals[1]), float(vals[2])
    return r == 0.0 and g == 0.0 and b == 0.0


def _create_material(name, values, renderer, directory):
    Ka = Kd = Ks = Ke = Ns = Ni = illum = d = Tr = Tf = None
    map_Ka = map_Kd = map_Ks = map_d = None

    #TODO sampled spectrum
    if 'Ka' in values and not _zero_spectrum(values['Ka']):
        v = values['Ka']
        Ka = RGBSpectrum(float(v[0]), float(v[1]), float(v[2]))
    if 'Kd' in values and not _zero_spectrum(values['Kd']):
        v = values['Kd']
        Kd = RGBSpectrum(float(v[0]), float(v[1]), float(v[2]))
    if 'Ks' in values and not _zero_spectrum(values['Ks']):
        v = values['Ks']
        Ks = RGBSpectrum(float(v[0]), float(v[1]), float(v[2]))
    if 'Ke' in values and not _zero_spectrum(values['Ke']):
        v = values['Ke']
        Ke = RGBSpectrum(float(v[0]), float(v[1]), float(v[2]))
    if 'Ns' in values:
        Ns = float(values['Ns'][0])
    if 'Ni' in values:
        Ni = float(values['Ni'][0])
    if 'd' in values:
        d = float(values['d'][0])
    if 'Tr' in values:
        Tr = float(values['Tr'][0])
    if 'Tf' in values and not _zero_spectrum(values['Tf']):
        v = values['Tf']
        Tf = RGBSpectrum(float(v[0]), float(v[1]), float(v[2]))
    if 'illum' in values:
        illum = int(values['illum'][0])
    if 'map_Ka' in values:
        map_Ka = values['map_Ka'][0].strip()
    if 'map_Kd' in values:
        map_Kd = values['map_Kd'][0].strip()
    if 'map_Ks' in values:
        map_Ks = values['map_Ks'][0].strip()
    if 'map_d' in values:
        map_d = values['map_d'][0].strip()

    mat = Material()
    if map_Kd is not None: # lambertian texture
        full_path = os.path.join(directory, map_Kd)
        img = load_image(full_path)
        img_factory = lambda: type(img)(1, 1)
        mat.load('lambertian_texture', renderer.color_mgr, image_factory=img_factory)
        mat.set_value('texture', img)
    elif Ke is not None: # lambertian emission
        mat.load('lambertian_emiter', renderer.color_mgr)
        mat.set_value('emission', Ke)
        if Kd is None:
            Kd = RGBSpectrum(0.0, 0.0, 0.0)
        mat.set_value('diffuse', Kd)
    elif Ks is not None: # phong material
        mat.load('phong2', renderer.color_mgr)
        mat.set_value('specular', Ks)
        if Kd is None:
            Kd = RGBSpectrum(0.0, 0.0, 0.0)
        mat.set_value('diffuse', Kd)
        exponent = 1.0 if Ns is None else Ns
        mat.set_value('exponent', exponent)
    elif Kd is not None: # simple lambertian material
        mat.load('lambertian', renderer.color_mgr)
        mat.set_value('diffuse', Kd)
    elif Kd is None and Ks is None: #black lambertian
        mat.load('lambertian', renderer.color_mgr)
        Kd = RGBSpectrum(0.0, 0.0, 0.0)
        mat.set_value('diffuse', Kd)
    else:
        raise ValueError("Not sutuable material is found in mtl library", name)

    renderer.materials.add(name, mat)


def parse_matlib(fname, renderer):

    values = {}
    name = None

    fobj = open(fname)
    for line in fobj:
        line = line.strip()
        if line == "" or line[0] == '#': #skip blank lines and comments
            continue
        vals = line.split()
        if vals[0].strip() == 'newmtl':
            if name is not None:
                _create_material(name, values, renderer, os.path.dirname(fobj.name))
            values.clear()
            name = vals[1].strip()
            continue

        values[vals[0].strip()] = vals[1:]

    if name is not None:
        _create_material(name, values, renderer, os.path.dirname(fobj.name))



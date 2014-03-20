
import os.path
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
        Ka = RGBSpectrum(v[0], v[1], v[2])
    if 'Kd' in values and not _zero_spectrum(values['Kd']):
        v = values['Kd']
        Kd = RGBSpectrum(v[0], v[1], v[2])
    if 'Ks' in values and not _zero_spectrum(values['Ks']):
        v = values['Ks']
        Ks = RGBSpectrum(v[0], v[1], v[2])
    if 'Ke' in values and not _zero_spectrum(values['Ke']):
        v = values['Ke']
        Ke = RGBSpectrum(v[0], v[1], v[2])
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
        Tf = RGBSpectrum(v[0], v[1], v[2])
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
    if Kd is not None: # simple lambertian material
        mat.load('lambertian', renderer.sam_mgr, renderer.spectral)
        mat.set_value('diffuse', Kd)

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



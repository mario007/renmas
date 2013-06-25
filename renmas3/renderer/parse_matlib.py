
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

def _create_spectrum(vals, project):
    #assume RGB spectrum TODO xyz, sampled etc...
    r, g, b = float(vals[0]), float(vals[1]), float(vals[2])
    return project.col_mgr.create_spectrum((r, g, b))

def _create_material(name, values, project):
    Ka = Kd = Ks = Ns = illum = d = Tr = Tf = None
    map_Ka = map_Kd = map_Ks = map_d = None

    if 'Ka' in values:
        Ka = _create_spectrum(values['Ka'], project)
    if 'Kd' in values:
        Kd = _create_spectrum(values['Kd'], project)
    if 'Ks' in values:
        Ks = _create_spectrum(values['Ks'], project)
    if 'Ns' in values:
        Ns = float(values['Ns'][0])
    if 'd' in values:
        d = float(values['d'][0])
    if 'Tr' in values:
        Tr = float(values['Tr'][0])
    if 'Tf' in values:
        Tf = _create_spectrum(values['Tf'], project)
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

    props = {}
    #just basic lambertian for now
    if Kd is not None:
        props['diffuse'] = Kd
        mat = project.create_material(name, 'lambertian', props)
        project.mat_mgr.add(name, mat)

def parse_matlib(fobj, project):

    values = {}
    name = None

    for line in fobj:
        line = line.strip()
        if line == "" or line[0] == '#': #skip blank lines and comments
            continue
        vals = line.split()
        if vals[0].strip() == 'newmtl':
            if name is not None:
                _create_material(name, values, project)
            values.clear()
            name = vals[1].strip()
            continue

        values[vals[0].strip()] = vals[1:]

    if name is not None:
        _create_material(name, values, project)



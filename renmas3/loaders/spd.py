import os.path

def register_directory_spd(directory, typ):
    pass

def _load_values(fname):
    if not os.path.isfile(fname): return None #file doesn't exists
    f = open(fname)
    values = []
    for line in f:
        line = line.strip()
        if line == "" or line[0] == '#': continue
        words = line.split()
        if len(words) != 2: continue
        values.append((float(words[0]), float(words[1])))
    f.close()
    return values

def load_spd(name, typ):
    curdir = os.path.dirname(__file__)
    curdir, rest = os.path.split(curdir)

    if typ == 'light':
        fname = os.path.join(curdir, "spds", "lights", name + ".spd")
        return _load_values(fname)
    elif typ == 'metal':
        fname = os.path.join(curdir, "spds", "metals", name + "_n.spd")
        fname2 = os.path.join(curdir, "spds", "metals", name + "_k.spd")
        n = _load_values(fname)
        k = _load_values(fname2)
        return (n, k)
    elif typ == 'real_object':
        fname = os.path.join(curdir, "spds", "real_objects", name + ".spd")
        return _load_values(fname)

    return None


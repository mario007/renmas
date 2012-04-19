import os.path

class SPDLoader:
    def __init__(self):
        pass

    def load(self, type_name, object_name):
        curdir = os.path.dirname(__file__)
        curdir, rest = os.path.split(curdir)
        if type_name == "light":
            fname = os.path.join(curdir, "spds", "lights", object_name + ".spd")
            if os.path.isfile(fname):
                return self._load_spd_from_file(fname)
        elif type_name == "metal":
            fname1 = os.path.join(curdir, "spds", "metals", object_name + "_n.spd")
            fname2 = os.path.join(curdir, "spds", "metals", object_name + "_k.spd")
            if os.path.isfile(fname1) and os.path.isfile(fname2):
                n = self._load_spd_from_file(fname1)
                k = self._load_spd_from_file(fname2)
                return (n, k)
        elif type_name == "real_object":
            fname = os.path.join(curdir, "spds", "real_objects", object_name + ".spd")
            if os.path.isfile(fname):
                return self._load_spd_from_file(fname)
        return None

    def _load_spd_from_file(self, fname):
        f = open(fname)
        ret = self._load_spd(f)
        f.close()
        return ret

    def _load_spd(self, f):
        values = []
        for line in f:
            line = line.strip()
            if line == "": continue
            if line[0] == "#": continue
            words = line.split()
            if len(words) != 2: continue
            values.append((float(words[0]), float(words[1])))
        return values

    def register_directory(self, path_to_directory):
        pass


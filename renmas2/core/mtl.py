
import os
import os.path
from .material import Material
from .factory import Factory
from renmas2.materials import HemisphereCos

class Mtl:
    def __init__(self):
        pass

    def load(self, fname, renderer):
        if not os.path.exists(fname): return False

        f = open(fname, "r")
        self._kd = self._ks = self._ns = None
        self._name = None

        for line in f:
            line = line.strip()
            if line == "": continue # skip blank lines
            words = line.split()
            if words[0] == "newmtl":
                self._create_material(renderer)
                self._name = words[1]
            elif words[0] == "Kd":
                self._kd = (float(words[1]), float(words[2]), float(words[3]))
                pass
            elif words[0] == "Ks":
                self._ks = (float(words[1]), float(words[2]), float(words[3]))
                pass
            elif words[0] == "Ns":
                self._ns = (float(words[1]))

        self._create_material(renderer)
        f.close()

    def _create_material(self, ren):
        if self._kd is None and self._ks is None and self._ns is None:
            return
        factory = Factory()
        mat = Material(ren.converter.zero_spectrum())

        if self._ks is not None and self._kd is not None:
            diffuse = ren.converter.create_spectrum(self._kd)
            specular = ren.converter.create_spectrum(self._ks)
            lamb = factory.create_lambertian(diffuse)
            if self._ns is not None:
                phong_specular = factory.create_phong(specular, self._ns)
            else:
                phong_specular = factory.create_phong(specular, 1.0)
            mat.add(lamb)
            mat.add(phong_specular)
            sampling = HemisphereCos()
            mat.add(sampling)
            ren.add(self._name, mat)

        elif self._kd is not None:
            diffuse = ren.converter.create_spectrum(self._kd)
            lamb = factory.create_lambertian(diffuse)
            mat.add(lamb)
            sampling = HemisphereCos()
            mat.add(sampling)
            ren.add(self._name, mat)

        self._kd = self._ks = self._ns = None


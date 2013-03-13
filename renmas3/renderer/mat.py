
class Material:
    def __init__(self, brdf=None, btdf=None, bsdf=None, is_dielectric=False):
        self.brdf = brdf
        self.btdf = btdf
        self.bsdf = bsdf
        self.is_dielectric = is_dielectric


class MaterialManager:
    def __init__(self):
        self._materials = []
        self._materials_d = {}

    def add(self, name, material):
        if name in self._materials_d:
            raise ValueError("Material allready exist!")
        if not isinstance(material, Material):
            raise ValueError("Type error. Material is expected!", material)
        self._materials.append(material)
        self._materials_d[name] = material

    def remove(self, name):
        pass

    def mat_idx(self, name):
        if name not in self._materials_d:
            raise ValueError("Material doesn't exist!")
        m = self._materials_d[name]
        return self._materials.index(m)

    def prepare_brdfs(self, label, runtimes):
        for m in self._materials:
            m.prepare_brdf(runtimes)


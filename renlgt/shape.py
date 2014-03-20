
class MeshDesc:
    def __init__(self, vb, tb, name, material):
        self.vb = vb
        self.tb = tb
        self.name = name
        self.material = material

    def __repr__(self):
        return '<MeshDesc object at %s name=%s, mat_name=%s, nvertiecs=%i, ntriangles=%i>' % \
                (hex(id(self)), self.name, self.material, self.vb.size(), self.tb.size())


class FileDesc:
    def __init__(self, mesh_descs, material_file=None):
        self.mesh_descs = mesh_descs
        self.material_file = material_file


class DependencyShader:
    def __init__(self, shader, shaders=[]):
        self.shader = shader
        self.shaders = shaders

    def compile(self):
        for shader in self.shaders:
            shader.compile()
        shaders = []
        for shader in self.shaders:
            if isinstance(shader, DependencyShader):
                shaders.append(shader.shader)
            else:
                shaders.append(shader)
        self.shader.compile(shaders)

    def prepare(self, runtimes):
        for shader in self.shaders:
            shader.prepare(runtimes)
        self.shader.prepare(runtimes)


class Shape:

    def isect_b(self, ray, min_dist=99999.0):  # ray dir. must be normalized
        raise NotImplementedError()

    @classmethod
    def isect_b_shader(cls):
        raise NotImplementedError()

    def isect(self, ray, min_dist=999999.0):  # ray dir. must be normalized
        raise NotImplementedError()

    @classmethod
    def isect_shader(cls):
        raise NotImplementedError()

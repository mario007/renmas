
class MeshDesc:
    def __init__(self, vb, tb, name, material):
        self.vb = vb
        self.tb = tb
        self.name = name
        self.mat_name = material

    def __repr__(self):
        return '<MeshDesc object at %s name=%s, mat_name=%s, nvertiecs=%i, ntriangles=%i>' % \
                (hex(id(self)), self.name, self.mat_name, self.vb.size(), self.tb.size())




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

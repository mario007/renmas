
from renlight.sdl import register_struct, IntArg, FloatArg


class Sample:

    __slots__ = ['x', 'y', 'ix', 'iy', 'weight']

    def __init__(self, x, y, ix, iy, weight):
        self.x = x
        self.y = y
        self.ix = ix
        self.iy = iy
        self.weight = weight

    def __repr__(self):
        return 'x=%f y=%f ix=%i iy=%i weight=%f' % (self.x, self.y, self.ix,
                                                    self.iy, self.weight)

register_struct(Sample, 'Sample', fields=[('x', FloatArg),
                ('y', FloatArg), ('ix', IntArg), ('iy', IntArg),
                ('weight', FloatArg)],
                factory=lambda: Sample(0.0, 0.0, 0, 0, 0.0))

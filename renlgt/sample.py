
from sdl import register_struct, IntArg, FloatArg


class Sample:

    __slots__ = ['x', 'y', 'px', 'py', 'ix', 'iy', 'weight']

    def __init__(self, x, y, px, py, ix, iy, weight):
        self.x = x
        self.y = y
        self.px = px
        self.py = py
        self.ix = ix
        self.iy = iy
        self.weight = weight

    def __repr__(self):
        return 'x=%f y=%f px=%f py=%f ix=%i iy=%i weight=%f' % (self.x, self.y, self.px, self.py,
                                                                self.ix, self.iy, self.weight)

register_struct(Sample, 'Sample', fields=[('x', FloatArg),
                ('y', FloatArg), ('px', FloatArg), ('py', FloatArg),
                ('ix', IntArg), ('iy', IntArg), ('weight', FloatArg)],
                factory=lambda: Sample(0.0, 0.0, 0.0, 0.0, 0, 0, 0.0))

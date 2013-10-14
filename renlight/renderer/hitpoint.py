
from renlight.vector import Vector3
from renlight.sdl import register_struct, IntArg, FloatArg, Vec3Arg


class HitPoint:

    __slots__ = ['t', 'hit', 'normal', 'mat_idx', 'u', 'v']

    def __init__(self, t=0.0, hit=None, normal=None,
                 mat_idx=0, u=0.0, v=0.0):

        self.t = t
        self.hit = hit
        self.normal = normal
        self.mat_idx = mat_idx
        self.u = u
        self.v = v

register_struct(HitPoint, 'HitPoint', fields=[('t', FloatArg),
                ('hit', Vec3Arg), ('normal', Vec3Arg), ('mat_idx', IntArg),
                ('u', FloatArg), ('v', FloatArg)],
                factory=lambda: HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                                         Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0))

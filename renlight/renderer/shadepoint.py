
from renlight.vector import Vector3
from renlight.spectrum import RGBSpectrum
from renlight.sdl import register_struct
from renlight.sdl.args import FloatArg, Vec3Arg, RGBArg, SampledArg


class ShadePoint:

    __slots__ = ['wi', 'wo', 'pdf', 'material_reflectance']

    def __init__(self, wi=None, wo=None, pdf=None, material_reflectance=None):

        self.wi = wi
        self.wo = wo
        self.pdf = pdf
        self.material_reflectance = material_reflectance


def register_rgb_shadepoint():
    wi = Vector3(0.0, 0.0, 0.0)
    wo = Vector3(0.0, 0.0, 0.0)
    ref = RGBSpectrum(0.0, 0.0, 0.0)

    register_struct(ShadePoint, 'ShadePoint', fields=[('wi', Vec3Arg),
                    ('wo', Vec3Arg), ('pdf', FloatArg),
                    ('material_reflectance', RGBArg)],
                    factory=lambda: ShadePoint(wi, wo, 0.0, ref))


def register_sampled_shadepoint(col_mgr):
    wi = Vector3(0.0, 0.0, 0.0)
    wo = Vector3(0.0, 0.0, 0.0)
    ref = col_mgr.zero()
    register_struct(ShadePoint, 'ShadePoint', fields=[('wi', Vec3Arg),
                    ('wo', Vec3Arg), ('pdf', FloatArg),
                    ('material_reflectance', SampledArg)],
                    factory=lambda: ShadePoint(wi, wo, 0.0, ref))

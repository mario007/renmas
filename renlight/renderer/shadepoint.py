
from renlight.vector import Vector3
from renlight.spectrum import RGBSpectrum
from renlight.sdl import register_struct
from renlight.sdl.args import FloatArg, Vec3Arg, RGBArg, SampledArg,\
    StructArgPtr
from renlight.sdl.cgen import register_prototype
from .hitpoint import HitPoint


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

    wi = Vector3(0.0, 0.0, 0.0)
    wo = Vector3(0.0, 0.0, 0.0)
    ref = RGBSpectrum(0.0, 0.0, 0.0)
    sh = ShadePoint(wi, wo, 0.0, ref)
    hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sh)]

    register_prototype('material_reflectance', func_args=func_args)


def register_sampled_shadepoint(col_mgr):
    wi = Vector3(0.0, 0.0, 0.0)
    wo = Vector3(0.0, 0.0, 0.0)
    ref = col_mgr.zero()
    register_struct(ShadePoint, 'ShadePoint', fields=[('wi', Vec3Arg),
                    ('wo', Vec3Arg), ('pdf', FloatArg),
                    ('material_reflectance', SampledArg)],
                    factory=lambda: ShadePoint(wi, wo, 0.0, ref))

    wi = Vector3(0.0, 0.0, 0.0)
    wo = Vector3(0.0, 0.0, 0.0)
    ref = col_mgr.zero()
    sh = ShadePoint(wi, wo, 0.0, ref)
    hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sh)]

    register_prototype('material_reflectance', func_args=func_args)


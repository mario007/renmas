
from sdl import Vector3, RGBSpectrum, register_struct, FloatArg, Vec3Arg,\
    RGBArg, SampledArg, StructArgPtr

from sdl.cgen import register_prototype, spectrum_factory
from .hitpoint import HitPoint


class ShadePoint:

    __slots__ = ['wo', 'wi', 'light_intensity', 'light_position',
                 'material_reflectance', 'pdf']

    def __init__(self, wo=None, wi=None, light_intensity=None,
                 light_position=None, material_reflectance=None, pdf=None):

        self.wo = wo
        self.wi = wi
        self.light_intensity = light_intensity
        self.light_position = light_position
        self.material_reflectance = material_reflectance
        self.pdf = pdf


def register_rgb_class():
    wo = Vector3(0.0, 0.0, 0.0)
    wi = Vector3(0.0, 0.0, 0.0)
    li = RGBSpectrum(0.0, 0.0, 0.0)
    lpos = Vector3(0.0, 0.0, 0.0)
    ref = RGBSpectrum(0.0, 0.0, 0.0)

    register_struct(ShadePoint, 'ShadePoint', fields=[('wo', Vec3Arg),
                    ('wi', Vec3Arg), ('light_intensity', RGBArg),
                    ('light_position', Vec3Arg),
                    ('material_reflectance', RGBArg), ('pdf', FloatArg)],
                    factory=lambda: ShadePoint(wo, wi, li, lpos, ref, 0.0))


def register_sampled_class(col_mgr):
    wo = Vector3(0.0, 0.0, 0.0)
    wi = Vector3(0.0, 0.0, 0.0)
    li = col_mgr.zero()
    lpos = Vector3(0.0, 0.0, 0.0)
    ref = col_mgr.zero()

    register_struct(ShadePoint, 'ShadePoint', fields=[('wo', Vec3Arg),
                    ('wi', Vec3Arg), ('light_intensity', SampledArg),
                    ('light_position', Vec3Arg),
                    ('material_reflectance', SampledArg), ('pdf', FloatArg)],
                    factory=lambda: ShadePoint(wo, wi, li, lpos, ref, 0.0))


def register_rgb_light_prototype():
    wo = Vector3(0.0, 0.0, 0.0)
    wi = Vector3(0.0, 0.0, 0.0)
    li = RGBSpectrum(0.0, 0.0, 0.0)
    lpos = Vector3(0.0, 0.0, 0.0)
    ref = RGBSpectrum(0.0, 0.0, 0.0)

    hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                  Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    sp = ShadePoint(wo, wi, li, lpos, ref, 0.0)

    func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sp)]
    register_prototype('__light_radiance', func_args=func_args)


def register_sampled_light_prototype(col_mgr):

    wo = Vector3(0.0, 0.0, 0.0)
    wi = Vector3(0.0, 0.0, 0.0)
    li = col_mgr.zero()
    lpos = Vector3(0.0, 0.0, 0.0)
    ref = col_mgr.zero()

    hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                  Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    sp = ShadePoint(wo, wi, li, lpos, ref, 0.0)

    func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sp)]
    register_prototype('__light_radiance', func_args=func_args)


def register_rgb_material_prototype():
    wo = Vector3(0.0, 0.0, 0.0)
    wi = Vector3(0.0, 0.0, 0.0)
    li = RGBSpectrum(0.0, 0.0, 0.0)
    lpos = Vector3(0.0, 0.0, 0.0)
    ref = RGBSpectrum(0.0, 0.0, 0.0)

    hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                  Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    sp = ShadePoint(wo, wi, li, lpos, ref, 0.0)

    func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sp)]
    register_prototype('__material_reflectance', func_args=func_args)


def register_sampled_material_prototype(col_mgr):

    wo = Vector3(0.0, 0.0, 0.0)
    wi = Vector3(0.0, 0.0, 0.0)
    li = col_mgr.zero()
    lpos = Vector3(0.0, 0.0, 0.0)
    ref = col_mgr.zero()

    hp = HitPoint(0.0, Vector3(0.0, 0.0, 0.0),
                  Vector3(0.0, 0.0, 0.0), 0, 0.0, 0.0)
    sp = ShadePoint(wo, wi, li, lpos, ref, 0.0)

    func_args = [StructArgPtr('hitpoint', hp), StructArgPtr('shadepoint', sp)]
    register_prototype('__material_reflectance', func_args=func_args)


def register_rgb_shadepoint():
    register_rgb_class()
    register_rgb_light_prototype()
    register_rgb_material_prototype()
    spectrum_factory(lambda: RGBSpectrum(0.0, 0.0, 0.0))


def register_sampled_shadepoint(col_mgr):
    register_sampled_class(col_mgr)
    register_sampled_light_prototype(col_mgr)
    register_sampled_material_prototype(col_mgr)
    spectrum_factory(lambda: col_mgr.zero())

register_rgb_shadepoint()


from sdl import Vector3, RGBSpectrum, register_struct, FloatArg, Vec3Arg,\
    RGBArg, SampledArg, StructArgPtr

from sdl.cgen import register_prototype, spectrum_factory
from .hitpoint import HitPoint


class ShadePoint:

    __slots__ = ['wo', 'wi', 'light_intensity', 'light_position',
                 'material_reflectance', 'pdf', 'light_normal',
                 'light_pdf', 'material_emission']

    def __init__(self, wo=None, wi=None, light_intensity=None,
                 light_position=None, material_reflectance=None, pdf=None,
                 light_normal=None, light_pdf=None, material_emission=None):

        self.wo = wo
        self.wi = wi
        self.light_intensity = light_intensity
        self.light_position = light_position
        self.material_reflectance = material_reflectance
        self.pdf = pdf
        self.light_normal = light_normal
        self.light_pdf = light_pdf
        self.material_emission = material_emission

    @classmethod
    def factory(cls, spectrum):
        wo = Vector3(0.0, 0.0, 0.0)
        wi = Vector3(0.0, 0.0, 0.0)
        li = spectrum.zero()
        lpos = Vector3(0.0, 0.0, 0.0)
        ref = spectrum.zero()
        lnormal = Vector3(0.0, 1.0, 0.0)
        em = spectrum.zero()
        return ShadePoint(wo, wi, li, lpos, ref, 1.0, lnormal, 1.0, em)


def register_rgb_class():

    spectrum = RGBSpectrum(0.0, 0.0, 0.0)
    register_struct(ShadePoint, 'ShadePoint', fields=[
                    ('wo', Vec3Arg),
                    ('wi', Vec3Arg),
                    ('light_intensity', RGBArg),
                    ('light_position', Vec3Arg),
                    ('material_reflectance', RGBArg),
                    ('pdf', FloatArg),
                    ('light_normal', Vec3Arg),
                    ('light_pdf', FloatArg),
                    ('material_emission', RGBArg)],
                    factory=lambda: ShadePoint.factory(spectrum))


def register_sampled_class(col_mgr):
    spectrum = col_mgr.zero()
    register_struct(ShadePoint, 'ShadePoint', fields=[
                    ('wo', Vec3Arg),
                    ('wi', Vec3Arg),
                    ('light_intensity', SampledArg),
                    ('light_position', Vec3Arg),
                    ('material_reflectance', SampledArg),
                    ('pdf', FloatArg),
                    ('light_normal', Vec3Arg),
                    ('light_pdf', FloatArg),
                    ('material_emission', SampledArg)],
                    factory=lambda: ShadePoint.factory(spectrum))


def register_rgb_prototype(name):
    spectrum = RGBSpectrum(0.0, 0.0, 0.0)
    func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                 StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]
    register_prototype(name, func_args=func_args)


def register_sampled_prototype(col_mgr, name):
    spectrum = col_mgr.zero()
    func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                 StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]
    register_prototype(name, func_args=func_args)


def register_rgb_shadepoint():
    register_rgb_class()
    register_rgb_prototype('__material_reflectance')
    register_rgb_prototype('__light_radiance')
    register_rgb_prototype('__light_sample')
    register_rgb_prototype('__material_emission')
    register_rgb_prototype('__material_sampling')
    spectrum_factory(lambda: RGBSpectrum(0.0, 0.0, 0.0))


def register_sampled_shadepoint(col_mgr):
    register_sampled_class(col_mgr)
    register_sampled_prototype(col_mgr, '__material_reflectance')
    register_sampled_prototype(col_mgr, '__light_radiance')
    register_sampled_prototype(col_mgr, '__light_sample')
    register_sampled_prototype(col_mgr, '__material_emission')
    register_sampled_prototype(col_mgr, '__material_sampling')
    spectrum_factory(lambda: col_mgr.zero())

register_rgb_shadepoint()

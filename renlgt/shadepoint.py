
from sdl import Vector3, register_struct, FloatArg, Vec3Arg,\
    StructArgPtr, IntArg, arg_from_value
from sdl.cgen import register_prototype

from .hitpoint import HitPoint


class ShadePoint:

    __slots__ = ['wo', 'wi', 'light_intensity', 'light_position',
                 'material_reflectance', 'pdf', 'light_normal',
                 'light_pdf', 'material_emission', 'specular_bounce']

    def __init__(self, wo=None, wi=None, light_intensity=None,
                 light_position=None, material_reflectance=None, pdf=None,
                 light_normal=None, light_pdf=None, material_emission=None,
                 specular_bounce=None):

        self.wo = wo
        self.wi = wi
        self.light_intensity = light_intensity
        self.light_position = light_position
        self.material_reflectance = material_reflectance
        self.pdf = pdf
        self.light_normal = light_normal
        self.light_pdf = light_pdf
        self.material_emission = material_emission
        self.specular_bounce = specular_bounce

    @classmethod
    def factory(cls, spectrum):
        wo = Vector3(0.0, 0.0, 0.0)
        wi = Vector3(0.0, 0.0, 0.0)
        li = spectrum.zero()
        lpos = Vector3(0.0, 0.0, 0.0)
        ref = spectrum.zero()
        lnormal = Vector3(0.0, 1.0, 0.0)
        em = spectrum.zero()
        return ShadePoint(wo, wi, li, lpos, ref, 1.0, lnormal, 1.0, em, 0)


def register_shadepoint_class(spectrum):
    spec_arg = arg_from_value('dummy_name', spectrum)
    register_struct(ShadePoint, 'ShadePoint', fields=[
                    ('wo', Vec3Arg),
                    ('wi', Vec3Arg),
                    ('light_intensity', type(spec_arg)),
                    ('light_position', Vec3Arg),
                    ('material_reflectance', type(spec_arg)),
                    ('pdf', FloatArg),
                    ('light_normal', Vec3Arg),
                    ('light_pdf', FloatArg),
                    ('material_emission', type(spec_arg)),
                    ('specular_bounce', IntArg)],
                    factory=lambda: ShadePoint.factory(spectrum))


def _register_prototype(spectrum, name):
    func_args = [StructArgPtr('hitpoint', HitPoint.factory()),
                 StructArgPtr('shadepoint', ShadePoint.factory(spectrum))]
    register_prototype(name, func_args=func_args)


def register_prototypes(spectrum):
    register_shadepoint_class(spectrum)
    _register_prototype(spectrum, '__material_reflectance')
    _register_prototype(spectrum, '__light_radiance')
    _register_prototype(spectrum, '__light_sample')
    _register_prototype(spectrum, '__light_pdf')
    _register_prototype(spectrum, '__material_emission')
    _register_prototype(spectrum, '__material_sampling')
    _register_prototype(spectrum, '__material_pdf')
    _register_prototype(spectrum, '__light_emission')

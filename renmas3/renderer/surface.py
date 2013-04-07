from ..base import BaseShader, ArgumentMap, ArgumentList, register_user_type
from ..base import Spectrum, Vec3, Float, Integer, arg_list, arg_from_value
from ..shapes import HitPoint

class ShadePoint():
    __slots__ = ['light_intensity', 'light_position', 'material_emission', 'wi', 'wo','pdf',
            'material_spectrum', 'shape_pdf', 'shape_normal',
            'shape_sample', 'reflection_type']
    def __init__(self):
        self.light_intensity = None
        self.light_position = None
        self.material_emission = None
        self.wi = None
        self.wo = None
        self.pdf = None
        self.material_spectrum = None
        self.shape_pdf = None
        self.shape_normal = None
        self.shape_sample = None
        self.reflection_type = None

    @classmethod
    def user_type(cls):
        typ_name = "Shadepoint"
        fields = [('light_intensity', Spectrum), ('light_position', Vec3), ('material_emission', Spectrum),
                ('wi', Vec3), ('wo', Vec3), ('pdf', Float),
                ('material_spectrum', Spectrum), ('shape_pdf', Float), ('shape_normal', Vec3),
                ('shape_sample', Vec3), ('reflection_type', Integer)]
        return (typ_name, fields)

register_user_type(ShadePoint)

class SurfaceShader(BaseShader):
    def __init__(self, code, props, col_mgr):
        super(SurfaceShader, self).__init__(code)
        self._col_mgr = col_mgr
        self.props = props

    def standalone(self):
        return False

    def col_mgr(self):
        return self._col_mgr

    def get_props(self, nthreads):
        return self.props

    def arg_map(self):
        spectrum = self._col_mgr.black()
        args = ArgumentMap(arg_from_value(key, value, spectrum=spectrum)\
                                          for key, value in self.props.items())
        return args

    def arg_list(self):
        spectrum = self._col_mgr.black()
        return arg_list([('hitpoint', HitPoint), ('shadepoint', ShadePoint)], spectrum=spectrum)


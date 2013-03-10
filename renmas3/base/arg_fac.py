
import inspect
from .vector3 import Vector2, Vector3, Vector4
from .arg import Argument
from .integer import Integer, Float
from .vec234 import Vec2, Vec3, Vec4, Vec2I, Vec3I, Vec4I
from .usr_type import UserType, Struct, StructPtr
from .pointer import Pointer
from .spectrum import RGBSpectrum, SampledSpectrum, Spectrum
from .spec import RGBSpec, SampledSpec

def arg_from_value(name, value, input_arg=False, spectrum=None):
    """Create argument based on type of value."""

    if isinstance(value, int):
        arg = Integer(name, value)
    elif isinstance(value, float):
        arg = Float(name, value)
    elif isinstance(value, tuple) or isinstance(value, list):
        if len(value) > 4:
            raise ValueError('Vector is to big!', value)
        if len(value) == 2:
            arg = Vec2(name, Vector2(float(value[0]), float(value[1])))
        elif len(value) == 3:
            arg = Vec3(name, Vector3(float(value[0]), float(value[1]), float(value[2])))
        elif len(value) == 4:
            arg = Vec4(name, Vector4(float(value[0]), float(value[1]),
                                     float(value[2]), float(value[3])))
        else:
            raise ValueError('Vector is to small!', value)
    elif isinstance(value, Vector2):
        arg = Vec2(name, value)
    elif isinstance(value, Vector3):
        arg = Vec3(name, value)
    elif isinstance(value, Vector4):
        arg = Vec4(name, value)
    elif isinstance(value, RGBSpectrum):
        arg = RGBSpec(name, value)
    elif isinstance(value, SampledSpectrum):
        arg = SampledSpec(name, value)
    elif isinstance(value, UserType):
        if input_arg:
            arg = StructPtr(name, value)
        else:
            arg = Struct(name, value)
    elif hasattr(type(value), 'user_type'):
        typ_name, fields = type(value).user_type()
        usr_type = create_user_type(typ_name, fields, spectrum=spectrum)
        if input_arg:
            arg = StructPtr(name, usr_type)
        else:
            arg = Struct(name, usr_type)
    else:
        raise ValueError('Unknown value type', value)
    return arg

def arg_from_type(name, typ, value=None, input_arg=False, spectrum=None):
    """Create argument of specified type."""

    if typ == Integer:
        val = 0 if value is None else int(value)
        arg = Integer(name, val)
    elif typ == Float:
        val = 0.0 if value is None else float(value)
        arg = Float(name, val)
    elif typ == Vec2:
        val = Vector2(0.0, 0.0) if value is None else value
        arg = Vec2(name, val)
    elif typ == Vec3:
        val = Vector3(0.0, 0.0, 0.0) if value is None else value
        arg = Vec3(name, val)
    elif typ == Vec4:
        val = Vector4(0.0, 0.0, 0.0, 0.0) if value is None else value
        arg = Vec4(name, val)
    elif typ == Vec2I:
        val = Vector2I(0, 0) if value is None else value
        arg = Vec2I(name, val)
    elif typ == Vec3I:
        val = Vector3I(0, 0, 0) if value is None else value
        arg = Vec3I(name, val)
    elif typ == Vec4I:
        val = Vector4I(0, 0, 0, 0) if value is None else value
        arg = Vec4I(name, val)
    elif typ == Pointer: #pointer in typ = UserType
        arg = Pointer(name, typ=value)
    elif typ == Spectrum:
        if value is None and spectrum is None:
            arg = RGBSpec(name, RGBSpectrum(0.0, 0.0, 0.0))
        elif isinstance(value, (RGBSpectrum, SampledSpectrum)):
            arg = RGBSpec(name, value)
        elif spectrum is not None:
            if isinstance(spectrum, RGBSpectrum):
                arg = RGBSpec(name, spectrum.black())
            elif isinstance(spectrum, SampledSpectrum):
                arg = SampledSpec(name, spectrum.black())
            else:
                raise ValueError("Unknown spectrum type!", typ)
        else:
            raise ValueError("Cannot create desired spectrum!", typ)
    elif hasattr(typ, 'user_type'):
        typ_name, fields = typ.user_type()
        usr_type = create_user_type(typ_name, fields, spectrum=spectrum)
        if input_arg:
            arg = StructPtr(name, usr_type)
        else:
            arg = Struct(name, usr_type)
    else:
        print (name, typ, value, spectrum)
        raise ValueError("Unknown type of arugment", typ)

    return arg

def create_argument(name, value=None, typ=None, input_arg=False, spectrum=None):
    """Factory for creating argument based on value or based on type."""

    if value is None and typ is None:
        raise ValueError("Argument could not be created because type and value is None.")

    if typ is not None:
        return arg_from_type(name, typ, value, input_arg, spectrum=spectrum)

    return arg_from_value(name, value, input_arg, spectrum=spectrum)


#a5 = create_user_type_(typ="point", fields=[('x', 55)])
def create_user_type(typ, fields, spectrum=None):
    usr_type = UserType(typ)
    for n, v in fields:
        if inspect.isclass(v):
            arg = create_argument(n, typ=v, spectrum=spectrum)
        else:
            arg = create_argument(n, value=v, spectrum=spectrum)
        usr_type.add(arg)
    return usr_type



from .memcpy import memcpy
from .loader import Loader
from .shader import Shader
from .builtins import *
from .args import register_struct, Vec3Arg, StructArgPtr,\
    StructArg, PointerArg, ArgList, arg_from_value, get_struct_desc, Vec4Arg


from .ray import Ray
from .vector import Vector2, Vector3, Vector4
from .image import ImageRGBA, ImagePRGBA
from .spectrum import RGBSpectrum, SampledSpectrum, SampledManager, RGBManager

register_struct(Ray, 'Ray', fields=[('origin', Vec3Arg),
                ('direction', Vec3Arg)],
                factory=lambda: Ray(Vector3(0.0, 0.0, 0.0),
                                    Vector3(0.0, 0.0, 0.0)))

register_struct(ImageRGBA, 'ImageRGBA', fields=[('width', IntArg),
                ('height', IntArg), ('pitch', IntArg), ('pixels', PointerArg)],
                factory=lambda: ImageRGBA(1, 1))

register_struct(ImagePRGBA, 'ImagePRGBA', fields=[('width', IntArg),
                ('height', IntArg), ('pitch', IntArg), ('pixels', PointerArg)],
                factory=lambda: ImagePRGBA(1, 1))

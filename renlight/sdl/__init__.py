

from .loader import Loader
from .shader import Shader
from .builtins import *
from .args import register_struct, Vec3Arg, StructArgPtr, StructArg, PointerArg


from renlight.ray import Ray
from renlight.vector import Vector3
from renlight.image import ImageRGBA, ImagePRGBA

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

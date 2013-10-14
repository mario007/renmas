

from .loader import Loader
from .shader import Shader
from .builtins import *
from .args import register_struct, Vec3Arg, StructArgPtr, StructArg


from renlight.ray import Ray
from renlight.vector import Vector3

register_struct(Ray, 'Ray', fields=[('origin', Vec3Arg),
                ('direction', Vec3Arg)],
                factory=lambda: Ray(Vector3(0.0, 0.0, 0.0),
                                    Vector3(0.0, 0.0, 0.0)))


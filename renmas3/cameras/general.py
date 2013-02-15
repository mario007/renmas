
from ..base import Vector3, create_shader, arg_map, arg_list, Vec3, Float
from ..base import Ray, BaseShader
from ..samplers import Sample

class Camera(BaseShader):
    """General shader for camera."""

    def __init__(self, eye, lookat, distance, code):
        super(Camera, self).__init__(code)
        self._eye = eye
        self._lookat = lookat
        self._up = Vector3(0.0, 1.0, 0.0)
        self._distance = float(distance) #distance of image plane form eye point
        self._compute_uvw()

    def _compute_uvw(self):
        self._w = self._eye - self._lookat #w is in oposite direction of view
        self._w.normalize()
        self._u = self._up.cross(self._w)
        self._u.normalize()
        self._v = self._w.cross(self._u)
        #singularity
        if self._eye.x == self._lookat.x and self._eye.z == self._lookat.z\
                and self._eye.y > self._lookat.y: #camera looking vertically down
            self._u = Vector3(0.0, 0.0, 1.0)
            self._v = Vector3(1.0, 0.0, 0.0)
            self._w = Vector3(0.0, 1.0, 0.0)

        if self._eye.x == self._lookat.x and self._eye.z == self._lookat.z\
                and self._eye.y < self._lookat.y: #camera looking vertically up
            self._u = Vector3(1.0, 0.0, 0.0)
            self._v = Vector3(0.0, 0.0, 1.0)
            self._w = Vector3(0.0, -1.0, 0.0)

    def get_props(self, nthreads):
        props = {}
        props['eye'] = self._eye
        props['lookat'] = self._lookat
        props['up'] = self._up
        props['distance'] = self._distance
        props['u'] = self._u
        props['v'] = self._v
        props['w'] = self._w
        return props

    def arg_map(self):
        args = arg_map([('u', Vec3), ('v', Vec3), ('w', Vec3), ('distance', Float),
                        ('eye', Vec3), ('lookat', Vec3), ('up', Vec3)])
        return args

    def arg_list(self):
        return arg_list([('sample', Sample), ('ray', Ray)])

    def method_name(self):
        return 'generate_ray'

    def standalone(self):
        return False


def create_perspective_camera(eye, lookat, distance):
    code = """
tmp1 = u * sample.x
tmp2 = v * sample.y
tmp3 = w * distance
direction = tmp1 + tmp2 - tmp3
ray.origin = eye
ray.dir =  normalize(direction)

    """

    camera = Camera(eye, lookat, distance, code=code)
    return camera
    


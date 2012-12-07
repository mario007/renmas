
from ..base import Vector3, create_shader, arg_map, arg_list, Vec3, Float
from ..base import Ray
from ..samplers import Sample

class GeneralCamera:
    def __init__(self, eye, lookat, distance=100, py_code=None, code=None):
        self._eye = eye
        self._lookat = lookat
        self._up = Vector3(0.0, 1.0, 0.0)
        self._distance = float(distance) #distance of image plane form eye point
        self._py_code = py_code
        self._code = code
        self._compute_uvw()
        self._props = {}
        self._update_props()
        self._shader = None

    def _compute_uvw(self):
        self._w = self._eye - self._lookat #w is in oposite direction of view
        self._w.normalize()
        self._u = self._up.cross(self._w)
        self._u.normalize()
        self._v = self._w.cross(self._u)
        #singularity
        if self._eye.x == self._lookat.x and self._eye.z == self._lookat.z and self._eye.y > self._lookat.y: #camera looking vertically down
            self._u = Vector3(0.0, 0.0, 1.0)
            self._v = Vector3(1.0, 0.0, 0.0)
            self._w = Vector3(0.0, 1.0, 0.0)

        if self._eye.x == self._lookat.x and self._eye.z == self._lookat.z and self._eye.y < self._lookat.y: #camera looking vertically up
            self._u = Vector3(1.0, 0.0, 0.0)
            self._v = Vector3(0.0, 0.0, 1.0)
            self._w = Vector3(0.0, -1.0, 0.0)

    def prepare(self, runtimes, shaders=None):
        
        _arg_map = arg_map([('u', Vec3), ('v', Vec3), ('w', Vec3),
            ('distance', Float), ('eye', Vec3), ('lookat', Vec3),
            ('up', Vec3)])
        _arg_list = arg_list([('sample', Sample), ('ray', Ray)])
        self._shader = create_shader("generate_ray", self._code, _arg_map,
                input_args=_arg_list, func=True)

        self._shader.prepare(runtimes)

        for idx in range(len(runtimes)):
            self._shader.set_value('eye', self._eye, idx_thread=idx)
            self._shader.set_value('up', self._up, idx_thread=idx)
            self._shader.set_value('lookat', self._lookat, idx_thread=idx)
            self._shader.set_value('u', self._u, idx_thread=idx)
            self._shader.set_value('v', self._v, idx_thread=idx)
            self._shader.set_value('w', self._w, idx_thread=idx)
            self._shader.set_value('distance', self._distance, idx_thread=idx)

        #print(self._shader._code)
        #def create_shader(name, source, args, input_args=[], shaders=[], func=False):
        pass
    
    @property
    def shader(self):
        return self._shader

    def _update_props(self):
        self._props['eye'] = self._eye
        self._props['lookat'] = self._lookat
        self._props['up'] = self._up
        self._props['distance'] = self._distance
        self._props['u'] = self._u
        self._props['v'] = self._v
        self._props['w'] = self._w

    def generate_ray(self, sample):
        return self._py_code(self._props, sample)


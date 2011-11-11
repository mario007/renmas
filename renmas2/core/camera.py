
from .vector3 import Vector3
from .dynamic_array import DynamicArray
from .structures import Structures
import x86
from tdasm import Runtime
from ..macros import macro_call, assembler

class Camera:
    def __init__(self, eye, lookat, distance=100):
        self.eye = Vector3(float(eye[0]), float(eye[1]), float(eye[2]))
        self.lookat = Vector3(float(lookat[0]), float(lookat[1]), float(lookat[2]))
        self.up = Vector3(0.0, 1.0, 0.0)
        self.distance = float(distance) #distance of image plane form eye point
        self._compute_uvw()
        self.structures = Structures()

        self._ds = None

    def _compute_uvw(self):
        self.w = self.eye - self.lookat #w is in oposite direction of view
        self.w.normalize()
        self.u = self.up.cross(self.w)
        self.u.normalize()
        self.v = self.w.cross(self.u)
        #singularity
        if self.eye.x == self.lookat.x and self.eye.z == self.lookat.z and self.eye.y > self.lookat.y: #camera looking vertically down
            self.u = Vector3(0.0, 0.0, 1.0)
            self.v = Vector3(1.0, 0.0, 0.0)
            self.w = Vector3(0.0, 1.0, 0.0)

        if self.eye.x == self.lookat.x and self.eye.z == self.lookat.z and self.eye.y < self.lookat.y: #camera looking vertically up
            self.u = Vector3(1.0, 0.0, 0.0)
            self.v = Vector3(0.0, 0.0, 1.0)
            self.w = Vector3(0.0, -1.0, 0.0)

    def set_eye(self, x, y, z):
        self.eye = renmas.maths.Vector3(float(x), float(y), float(z))
        self._update_camera()

    def set_lookat(self, x, y, z):
        self.lookat = renmas.maths.Vector3(float(x), float(y), float(z))
        self._update_camera()

    def set_distance(self, distance):
        self.distance = float(distance)
        self._update_camera()

    def generate_ray(self, sample, origin, direction):
        raise NotImplementedError()

    def generate_ray_asm(self, runtimes, label):
        raise NotImplementedError()

    def _update_data(self):
        pass

    def _update_camera(self):
        self._compute_uvw()
        self._update_data()


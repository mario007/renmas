
from ..core import Vector3

class Camera:
    def __init__(self, eye, lookat, distance=100):
        self.eye = Vector3(float(eye[0]), float(eye[1]), float(eye[2]))
        self.lookat = Vector3(float(lookat[0]), float(lookat[1]), float(lookat[2]))
        self.up = Vector3(0.0, 1.0, 0.0)
        self.distance = float(distance) #distance of image plane form eye point
        self._compute_uvw()

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

    def get_eye(self):
        return (self.eye.x, self.eye.y, self.eye.z)

    def get_lookat(self):
        return (self.lookat.x, self.lookat.y, self.lookat.z)

    def get_distance(self):
        return self.distance

    def _float(self, old, new):
        try:
            return float(new)
        except:
            return old 

    def set_eye(self, x, y, z):
        eye = self.eye
        self.eye = Vector3(self._float(eye.x, x), self._float(eye.y, y), self._float(eye.z, z))
        self._update_camera()

    def set_lookat(self, x, y, z):
        lookat = self.lookat
        self.lookat = Vector3(self._float(lookat.x, x), self._float(lookat.y, y), self._float(lookat.z, z))
        self._update_camera()

    def camera_moved(self, edx, edy, edz, ldx, ldy, ldz):#regulation of distance is missing for now TODO not tested
        self.eye.x += edx
        self.eye.y += edy
        self.eye.z += edz
        self.lookat.x += ldx
        self.lookat.y += ldy
        self.lookat.z += ldz
        self._update_camera()

    def set_distance(self, distance):
        self.distance = self._float(self.distance, distance)
        self._update_camera()

    def ray(self, sample):
        raise NotImplementedError()

    def ray_asm(self, runtimes, label):
        raise NotImplementedError()

    def _update_data(self):
        raise NotImplementedError()

    def _update_camera(self):
        self._compute_uvw()
        self._update_data()


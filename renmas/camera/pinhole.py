import renmas.core
import renmas.maths

class PinholeCamera:
    def __init__(self, eye, lookat, distance=100):
        self.eye = eye
        self.lookat = lookat
        self.up = renmas.maths.Vector3(0.0, 1.0, 0.0)
        self.distance = distance #distance of image plane form eye point
        self.compute_uvw()

    def compute_uvw(self):
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

    def ray(self, sample):
        direction = self.u * sample.x + self.v * sample.y - self.w * self.distance
        direction.normalize()
        return renmas.core.Ray(self.eye, direction)


